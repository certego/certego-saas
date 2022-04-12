import time


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


import logging

logger = logging.getLogger(__name__)


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
