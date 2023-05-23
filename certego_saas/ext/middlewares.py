import logging
import time

from django.conf import settings
from django.http.response import Http404

logger = logging.getLogger(__name__)


class StatsMiddleware:
    """
    Install this middleware if you are using
    :meth:`certego_saas.ext.exceptions.custom_exception_handler`.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.x_request_time = time.time()  # used in exception logging
        return self.get_response(request)


class LogMiddleware:
    """
    Install this middleware if you want to add basic logging to your API endpoints
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        logger.info(
            f"request {request.method} {request.path} received from {request.user}"
        )

        response = self.get_response(request)

        logger.info(f"response {request.method} {request.path} sent to {request.user}")

        # Code to be executed for each request/response after
        # the view is called.

        return response


class BlockListForwardedForMiddleware:
    """
    Every request that has the X-Forwarded-From set as an ip in BLOCKLIST_FORWARDED_FOR returns 404
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        remote_addr = request.headers.get("X-Forwarded-For", "")
        try:
            blocklist = settings.BLOCKLIST_FORWARDED_FOR
        except AttributeError:
            blocklist = []
        if remote_addr in blocklist:
            raise Http404(f"Request has X-Forwarded-For set to {remote_addr}: blocked")

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
