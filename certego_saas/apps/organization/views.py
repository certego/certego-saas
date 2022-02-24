from django.db.models import Prefetch
from rest_flex_fields import is_expanded
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from certego_saas.ext.viewsets import ListAndDeleteOnlyViewSet

from .invitation import Invitation
from .membership import Membership
from .organization import Organization
from .permissions import (
    InvitationDestroyObjectPermission,
    IsObjectOwnerPermission,
    IsObjectSameOrgPermission,
)
from .serializers import (
    InvitationsListSerializer,
    InviteCreateSerializer,
    OrganizationSerializer,
)

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
            permissions.append(IsObjectOwnerPermission())
        elif self.action in ["list", "retrieve", "leave"]:
            permissions.append(IsObjectSameOrgPermission())
        return permissions

    def list(self, request):
        """
        Get organization.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request):
        """
        Create new organization.
        """
        if request.user.has_membership():
            raise Membership.ExistingMembershipException()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, *args, **kwargs):
        """
        Delete organization (accessible only to the organization owner).
        """
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def invite(self, request, *args, **kwargs):
        """
        Invite user to organization (accessible only to the organization owner).

        ``POST ~/organization/invite``.
        """
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
        Remove user's membership from organization (accessible only to the organization owner).

        ``POST ~/organization/remove_member``.
        """
        username = request.data.get("username", None)
        if not username:
            raise ValidationError("'username' is required.")
        org = self.get_object()
        try:
            membership = org.members.get(user__username=username)
            if membership.is_owner:
                raise ValidationError("Cannot remove organization owner.")
        except Membership.DoesNotExist:
            raise ValidationError("No such member.")
        membership.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def leave(self, request, *args, **kwargs):
        """
        Leave organization (accessible only to members).

        ``POST ~/organization/leave``.
        """
        if request.user.membership.is_owner:
            raise Membership.OwnerCantLeaveException()
        request.user.membership.delete()
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
    def accept(self, *args, **kwargs):
        """
        Accept an invitation by ID.
        """
        instance: Invitation = self.get_object()
        instance.accept()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST"],
    )
    def decline(self, *args, **kwargs):
        """
        Decline an invitation by ID.
        """
        instance: Invitation = self.get_object()
        instance.decline()
        return Response(status=status.HTTP_204_NO_CONTENT)
