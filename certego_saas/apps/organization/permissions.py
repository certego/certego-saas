from rest_framework.permissions import BasePermission

from .invitation import Invitation
from .membership import Membership
from .organization import Organization


class InvitationDestroyObjectPermission(BasePermission):
    """
    Only the organization who created the invitation in the first place
    can delete the invitation provided that the invitation status is "PENDING"
    """

    message = "Invitation was previously accepted or declined so cannot be deleted."

    def has_object_permission(self, request, view, obj: Invitation):
        is_pending = obj.is_pending()
        try:
            Membership.objects.get(
                user__username=request.user,
                organization=obj.organization,
                is_admin=True,
            )
        except Membership.DoesNotExist:
            return False
        return is_pending


class IsObjectOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Organization):
            return obj.owner == request.user
        if obj_owner := getattr(obj, "user", None):
            return obj_owner == request.user
        return False


class IsObjectAdminPermission(BasePermission):
    def has_object_permission(self, request, view, obj: Organization):
        try:
            return Membership.objects.get(
                user__username=request.user, organization=obj, is_admin=True
            )
        except Membership.DoesNotExist:
            return False


class IsObjectSameOrgPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Organization):
            return obj.user_has_membership(request.user)
        if obj_owner := getattr(obj, "user", None):
            return (
                obj_owner.has_membership()
                and request.user.has_membership()
                and obj_owner.membership.organization_id
                == request.user.membership.organization_id
            )
        return False


class IsObjectCertegoOrgPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj_owner := getattr(obj, "user", None):
            return (
                obj_owner.has_membership()
                and obj_owner.membership.organization_id == Organization.certego().pk
            )
        return False


IsObjectOwnerOrCertegoOrgPermission = (
    IsObjectOwnerPermission | IsObjectCertegoOrgPermission  # pylint: disable=E1131
)
IsObjectOwnerOrSameOrgPermission = (
    IsObjectOwnerPermission | IsObjectSameOrgPermission  # pylint: disable=E1131
)

IsObjectOwnerOrSameOrgOrCertegoOrgPermission = (
    IsObjectOwnerPermission  # pylint: disable=E1131
    | IsObjectSameOrgPermission  # pylint: disable=E1131
    | IsObjectCertegoOrgPermission  # pylint: disable=E1131
)
