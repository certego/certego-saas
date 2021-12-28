from rest_framework.exceptions import APIException, PermissionDenied

__all__ = [
    "CustomerWithoutSubscription",
    "CustomerCantSubmitPrivateException",
    "CustomerCantSubmitMultipleProfilesException",
]


class CustomerWithoutSubscription(APIException):
    """
    Raised when a given user/customer
    has no active subscription on stripe.
    """

    status_code = 403
    default_detail = "You do not have an active paid subscription for this service."

    def __init__(self, appname: str, detail=None, code=None):
        self.default_detail = (
            f"You do not have an active paid subscription for service '{appname}'"
        )
        super().__init__(detail=detail, code=code)


class CustomerCantSubmitPrivateException(PermissionDenied):
    status_code = 400
    default_detail = "Your current plan does not allow for 'private' submissions. Please re-submit the analysis with private=False."


class CustomerCantSubmitMultipleProfilesException(PermissionDenied):
    status_code = 400
    default_detail = "Your current plan does not allow for these many concurrent profiles. Please re-submit the analysis with the correct number of profiles."
