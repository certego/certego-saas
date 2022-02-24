from rest_framework.permissions import BasePermission


class UserHasActiveSubscription(BasePermission):
    """
    Allows access to customers who have an active stripe subscription.

    * Should be used along with :class:`rest_framework.permissions.IsAuthenticated`.
    """

    message = {
        "error": "Permission Denied",
        "detail": "Customer does not have an active paid subscription.",
    }
    code = 403

    def has_permission(self, request, view):
        if not hasattr(request, "user"):
            return False

        # this is just as a "better safe than sorry" measure
        if not request.user.is_active:
            return False

        if request.user.has_customer():
            return (
                request.user.customer.currentapp_subscription.has_active_subscription()
            )
        return False
