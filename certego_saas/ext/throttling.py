"""
`DRF throttling <https://www.django-rest-framework.org/api-guide/throttling/>`__
"""
from typing import List, Union

from django.conf import settings
from rest_framework.throttling import UserRateThrottle


class _CustomUserRateThrottle(UserRateThrottle):
    """
    Extends DRF's ``UserRateThrottle`` to,
    - perform scoped throttling on per view-action combination basis.
    - disable throttling if running in internal deployment.
    - disable throttling if request method does not match.
    """

    cache_format = "throttle.userId_%(ident)s.%(scope)s"
    throttle_methods: Union[List[str], str] = "__all__"

    def get_cache_key(self, request, view):
        key = (
            super(_CustomUserRateThrottle, self).get_cache_key(request, view)
            + "."
            + f"{view.__class__.__name__}_{getattr(view, 'action', request.method)}"
        )
        return key

    def allow_request(self, request, view):
        if not settings.PUBLIC_DEPLOYMENT:
            return True
        if (
            request.method != "__all__"
            and request.method.lower() not in self.throttle_methods
        ):
            return True
        return super(_CustomUserRateThrottle, self).allow_request(request, view)


class POSTModelUserRateThrottle(_CustomUserRateThrottle):
    scope = "POST_model"
    throttle_methods = ["post"]

    def get_rate(self):
        return "15/min"


class DELETEModelUserRateThrottle(_CustomUserRateThrottle):
    scope = "DELETE_model"
    throttle_methods = ["delete"]

    def get_rate(self):
        return "15/min"


class PATCHModelUserRateThrottle(_CustomUserRateThrottle):
    scope = "PUTPATCH_model"
    throttle_methods = ["patch", "put"]

    def get_rate(self):
        return "15/min"


class POSTUserRateThrottle(_CustomUserRateThrottle):
    scope = "POST_default"
    throttle_methods = ["post"]

    def get_rate(self):
        return "5/h"
