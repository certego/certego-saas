"""
`DRF throttling <https://www.django-rest-framework.org/api-guide/throttling/>`__
"""

from django.conf import settings
from rest_framework.throttling import UserRateThrottle


class _CustomUserRateThrottle(UserRateThrottle):
    cache_format = "throttle.userId_%(ident)s.%(scope)s"

    def get_cache_key(self, request, view):
        key = (
            super(_CustomUserRateThrottle, self).get_cache_key(request, view)
            + "."
            + f"{view.__class__.__name__}_{getattr(view, 'action', request.method)}"
        )
        return key

    def allow_request(self, request, view):
        """
        Overriden to disable throttling if running in internal deployment.
        """
        if not settings.PUBLIC_DEPLOYMENT:
            return True
        return super(_CustomUserRateThrottle, self).allow_request(request, view)


class POSTModelUserRateThrottle(_CustomUserRateThrottle):
    scope = "POST_model"

    def allow_request(self, request, view):
        if request.method == "POST":
            return super().allow_request(request, view)
        return True

    def get_rate(self):
        return "15/min"


class DELETEModelUserRateThrottle(_CustomUserRateThrottle):
    scope = "DELETE_model"

    def allow_request(self, request, view):
        if request.method == "DELETE":
            return super().allow_request(request, view)
        return True

    def get_rate(self):
        return "15/min"


class PATCHModelUserRateThrottle(_CustomUserRateThrottle):
    scope = "PUTPATCH_model"

    def allow_request(self, request, view):
        if request.method in ["PATCH", "PUT"]:
            return super().allow_request(request, view)
        return True

    def get_rate(self):
        return "15/min"


class POSTUserRateThrottle(_CustomUserRateThrottle):
    scope = "POST_default"

    def allow_request(self, request, view):
        if request.method == "POST":
            return super(POSTUserRateThrottle, self).allow_request(request, view)
        return True

    def get_rate(self):
        return "5/h"
