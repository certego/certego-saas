import ast
import ipaddress
import logging
import time
from typing import Set, Union

from django_user_agents.utils import get_user_agent

logger = logging.getLogger(__name__)

DEFAULT_SENSITIVE_FIELDS = {
    "api",
    "token",
    "key",
    "secret",
    "password",
    "signature",
    "recaptcha",
}


class LogBuilder:
    """Builds log object using
    ``request``, ``response``, ``view``, ``exception``
    data and logs it.

    Based on: https://github.com/lingster/drf-api-tracking
    """

    CLEANED_SUBSTITUTE = "********"

    logging_methods = "__all__"
    __sensitive_fields: Set[str] = set()

    def __init__(self, request, response, view, exception=None):
        assert isinstance(
            self.CLEANED_SUBSTITUTE, str
        ), "CLEANED_SUBSTITUTE must be a string."
        self.request = request
        self.response = response
        self.view = view
        self.exception = exception
        self.log = {}

    @property
    def sensitive_fields(self):
        return self.__sensitive_fields

    @sensitive_fields.setter
    def sensitive_fields(self, value):
        self.__sensitive_fields = DEFAULT_SENSITIVE_FIELDS | {
            field.lower() for field in value
        }

    def build_log(self):
        if hasattr(self.response, "data"):
            response_data = self.response.data
        else:
            response_data = None

        user = self._get_user()
        self.log.update(
            {
                **self._get_request_response_time(),
                "user": user,
                "username_persistent": user.get_username() if user else None,
                "method": self.request.method.upper(),
                "status_code": self.response.status_code,
                "path": self.request.path,
                "remote_addr": self._get_ip_address(),
                "host": self.request.get_host(),
                "query_params": self._clean_data(self.request.query_params.dict()),
                "view": self._get_view_name(),
                "body": self._get_request_data(),
                "response": self._clean_data(response_data),
                "errors": self._get_errors() if self.exception else None,
            }
        )

    def handle_log(self):
        """
        Hook to define what happens with the log.
        """
        if self.should_log():
            logger.log(logging.ERROR, self.log)

    def should_log(self) -> bool:
        """
        Method that should return a value that evaluated to True if the request should be logged.
        By default, check if the request method is in logging_methods.
        """
        return (
            self.logging_methods == "__all__"
            or self.request.method in self.logging_methods
        )

    def _get_request_response_time(self) -> dict:
        requested_at = getattr(self.request, "x_request_time", None)
        if not requested_at:
            return {}

        response_ms = int((time.time() - requested_at) * 1000)

        return {
            "requested_at": int(requested_at),
            "response_ms": response_ms,
        }

    def _get_request_data(self) -> dict:
        # self.log["data"] = self._clean_data(request.body)
        try:
            # Accessing request.data *for the first time* parses the request body, which may raise
            # ParseError and UnsupportedMediaType exceptions. It's important not to swallow these,
            # as (depending on implementation details) they may only get raised this once, and
            # DRF logic needs them to be raised by the view for error handling to work correctly.
            data = self.request.data.dict()
        except AttributeError:
            data = self.request.data

        return self._clean_data(data)

    def _get_errors(self) -> Union[str, None]:
        return str(self.exception) if self.exception else None

    def _get_ip_address(self) -> str:
        """Get the remote ip address the request was generated from."""
        ipaddr = self.request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ipaddr:
            ipaddr = ipaddr.split(",")[0]
        else:
            ipaddr = self.request.META.get("REMOTE_ADDR", "")

        # Account for IPv4 and IPv6 addresses, each possibly with port appended. Possibilities are:
        # <ipv4 address>
        # <ipv6 address>
        # <ipv4 address>:port
        # [<ipv6 address>]:port
        # Note that ipv6 addresses are colon separated hex numbers
        possibles = (ipaddr.lstrip("[").split("]")[0], ipaddr.split(":")[0])

        for addr in possibles:
            try:
                return str(ipaddress.ip_address(addr))
            except ValueError:
                pass

        return ipaddr

    def _get_view_name(self) -> Union[str, None]:
        """Get view name."""
        view = getattr(self, "view", None)
        if view:
            return view.__module__ + "." + view.__class__.__name__
            # return view.get_view_name()
        return None

    def _get_user(self) -> Union[None, "User"]:  # type: ignore
        """Get user."""
        user = getattr(self.request, "user", None)
        if user and user.is_anonymous:
            return None
        return user

    def _get_user_agent(self) -> Union[str, None]:
        """Get user-agent string"""
        user_agent = get_user_agent(self.request)
        return str(user_agent) if user_agent else None

    def _clean_data(self, data):
        """
        Clean a dictionary of data of potentially sensitive info before
        sending to the database.
        Function based on the "_clean_credentials" function of django
        (https://github.com/django/django/blob/stable/1.11.x/django/contrib/auth/__init__.py#L50)

        Fields defined by django are by default cleaned with this function

        You can define your own sensitive fields in your view by defining a set
        eg: sensitive_fields = {'field1', 'field2'}
        """
        if isinstance(data, bytes):
            data = data.decode(errors="replace")

        if isinstance(data, list):
            return [self._clean_data(d) for d in data]
        if isinstance(data, dict):
            data = dict(data)

            for key, value in data.items():
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError):
                    pass
                if isinstance(value, (list, dict)):
                    data[key] = self._clean_data(value)
                if key.lower() in self.sensitive_fields:
                    data[key] = self.CLEANED_SUBSTITUTE
        return data
