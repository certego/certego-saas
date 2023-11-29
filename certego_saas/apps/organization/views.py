import logging

from django.db.models import Prefetch
from rest_flex_fields import is_expanded
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from certego_saas.ext.viewsets import ListAndDeleteOnlyViewSet

from .invitation import Invitation
from .membership import Membership
from .organization import Organization
from .permissions import (
    InvitationDestroyObjectPermission,
    IsObjectAdminPermission,
    IsObjectOwnerPermission,
    IsObjectSameOrgPermission,
)
from .serializers import (
    AdminActionsSerializer,
    InvitationsListSerializer,
    InviteCreateSerializer,
    OrganizationSerializer,
)

logger = logging.getLogger(__name__)

__all__ = ["OrganizationViewSet", "InvitationViewSet"]


class OrganizationViewSet(GenericViewSet):
    """
    Manage auth user's organization.
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset().filter(members__user=self.request.user)
        if is_expanded(self.request, "members"):
            qs = qs.prefetch_related(
                Prefetch(
                    "members", queryset=Membership.objects.select_related("user").all()
                )
            )
        return qs

    def get_object(self) -> Organization:
        obj = self.get_queryset().first()
        if not obj:
            raise NotFound()
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.request.method.lower() in ["delete"]:
            permissions.append(IsObjectOwnerPermission())
        elif self.action in ["invite", "remove_member"]:
            permissions.append(IsObjectAdminPermission())
        elif self.action in ["list", "retrieve", "leave"]:
            permissions.append(IsObjectSameOrgPermission())
        return permissions

    def list(self, request):
        """
        Get organization.
        """
        logger.info(f"list organizations from user {request.user}")
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request):
        """
        Create new organization.
        """
        logger.info(f"create organizations from user {request.user}")
        if request.user.has_membership():
            raise Membership.ExistingMembershipException()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """
        Delete organization (accessible only to the organization owner).
        """
        logger.info(f"delete organizations from user {request.user}")
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def invite(self, request, *args, **kwargs):
        """
        Invite user to organization (accessible only to the organization admin).

        ``POST ~/organization/invite``.
        """
        logger.info(
            f"invite to organizations from user {request.user}. Data:{request.data}"
        )
        org = self.get_object()
        write_serializer = InviteCreateSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        write_serializer.is_valid(raise_exception=True)
        write_serializer.save(organization=org)
        read_serializer = InvitationsListSerializer(
            instance=write_serializer.instance, fields=["id", "status", "created_at"]
        )
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["POST"])
    def remove_member(self, request, *args, **kwargs):
        """
        Remove user's membership from organization (accessible only to the organization admin).

        ``POST ~/organization/remove_member``.
        """
        username_to_remove = request.data.get("username", None)
        logger.info(f"remove member {username_to_remove} from user {request.user}")
        if not username_to_remove:
            raise ValidationError("'username' is required.")
        org = self.get_object()
        try:
            membership_request_user = org.members.get(user__username=request.user)
            membership_user_to_remove = org.members.get(
                user__username=username_to_remove
            )
            if membership_user_to_remove.is_owner:
                raise PermissionDenied(
                    detail="Cannot remove organization owner.", code=403
                )
            # only the owner can remove the admin
            if (
                not membership_request_user.is_owner
                and membership_user_to_remove.is_admin
            ):
                raise PermissionDenied(detail="Cannot remove another admin.", code=403)
        except Membership.DoesNotExist:
            raise ValidationError("No such member.")
        membership_user_to_remove.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def leave(self, request, *args, **kwargs):
        """
        Leave organization (accessible only to members).

        ``POST ~/organization/leave``.
        """
        logger.info(f"leave membership org from user {request.user}")
        try:
            membership = request.user.membership
        except Membership.DoesNotExist:
            raise NotFound()
        if membership.is_owner:
            raise Membership.OwnerCantLeaveException()
        request.user.membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def promote_admin(self, request, *args, **kwargs):
        """
        Promote user as an admin of the org

        ``POST ~/organization/promote_admin``
        """
        username_to_promote = request.data.get("username", None)
        logger.info(f"promote {username_to_promote} as admin from user {request.user}")
        org = self.get_object()
        serializer = AdminActionsSerializer(
            data={
                "username": username_to_promote,
                "request_user_username": request.user.username,
            }
        )
        serializer.is_valid(raise_exception=True)
        membership_user_to_promote = org.members.get(user__username=username_to_promote)
        membership_user_to_promote.is_admin = True
        membership_user_to_promote.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=["POST"])
    def remove_admin(self, request, *args, **kwargs):
        """
        Remove user as admin of the org

        ``POST ~/organization/remove_admin``
        """
        username_to_remove = request.data.get("username", None)
        logger.info(f"remove {username_to_remove} as admin from user {request.user}")
        org = self.get_object()
        serializer = AdminActionsSerializer(
            data={
                "username": username_to_remove,
                "request_user_username": request.user.username,
            }
        )
        serializer.is_valid(raise_exception=True)
        membership_user_to_remove = org.members.get(user__username=username_to_remove)
        membership_user_to_remove.is_admin = False
        membership_user_to_remove.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InvitationViewSet(ListAndDeleteOnlyViewSet):
    queryset = (
        Invitation.objects.select_related("organization")
        .prefetch_related(
            Prefetch(
                "organization__members",
                queryset=Membership.objects.select_related("user").all(),
            )
        )
        .order_by("-created_at")
        .all()
    )
    serializer_class = InvitationsListSerializer
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "destroy":
            return qs
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        permissions = super(InvitationViewSet, self).get_permissions()
        if self.action == "destroy":
            return [*permissions, InvitationDestroyObjectPermission()]
        return [*permissions, IsObjectOwnerPermission()]

    def get_serializer(self, *args, **kwargs):
        return super().get_serializer(*args, **kwargs, omit=["user"])

    @action(
        detail=True,
        methods=["POST"],
    )
    def accept(self, request, *args, **kwargs):
        """
        Accept an invitation by ID.
        """
        logger.info(f"accept invitation to org from user {request.user}")
        instance: Invitation = self.get_object()
        instance.accept()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
    )
    def decline(self, request, *args, **kwargs):
        """
        Decline an invitation by ID.
        """
        logger.info(f"decline invitation to org from user {request.user}")
        instance: Invitation = self.get_object()
        instance.decline()
        return Response(status=status.HTTP_204_NO_CONTENT)
