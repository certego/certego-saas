import time


class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.x_request_time = time.time()  # used in exception logging
        return self.get_response(request)
