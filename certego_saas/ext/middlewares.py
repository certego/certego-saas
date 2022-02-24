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
