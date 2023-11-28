from rest_flex_fields.serializers import FlexFieldsModelSerializer
from rest_framework import serializers as rfs
from rest_framework.exceptions import NotFound, PermissionDenied

from certego_saas.apps.user.models import User
from certego_saas.apps.user.serializers import UserSerializer

from .invitation import Invitation
from .membership import Membership
from .organization import Organization

__all__ = [
    "OrganizationSerializer",
    "InvitationsListSerializer",
    "InviteCreateSerializer",
]


class _UserMemberSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Membership
        fields = ["username", "full_name", "joined", "is_admin"]

    joined = rfs.DateTimeField(source="created_at")
    username = rfs.CharField(source="user.username")
    full_name = rfs.CharField(source="user.get_full_name")


class OrganizationSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Organization
        exclude = ("id",)
        expandable_fields = {
            "members": (_UserMemberSerializer, {"many": True, "read_only": True}),
            "pending_invitations": (
                "certego_saas.apps.organization.InvitationsListSerializer",
                {
                    "fields": ["id", "user", "created_at"],
                    "many": True,
                },
            ),
        }

    members_count = rfs.IntegerField(read_only=True)
    owner = _UserMemberSerializer(source="owner_membership", read_only=True)
    is_user_owner = rfs.SerializerMethodField()

    def get_is_user_owner(self, obj) -> bool:
        user = self.context["request"].user
        return obj.owner.pk == user.pk

    def create(self, validated_data: dict) -> Organization:
        """
        Create :class:`~.models.Organization` object.
        """
        return Organization.create(
            name=validated_data["name"], owner=validated_data["owner"]
        )


class InvitationsListSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Invitation
        fields = rfs.ALL_FIELDS

    user = UserSerializer(fields=["username"])
    organization = OrganizationSerializer(
        fields=["name", "owner.username", "members_count"]
    )


class InviteCreateSerializer(rfs.Serializer):
    class Meta:
        fields = ["username"]

    username = rfs.CharField()

    def create(self, validated_data) -> Invitation:
        """
        Create :class:`~.models.Invitation` object.
        """
        request = self.context["request"]
        username: str = validated_data.get("username")
        org: Organization = validated_data.get("organization")

        try:
            invitee = User.objects.get(username=username)
        except User.DoesNotExist:
            raise rfs.ValidationError({"detail": "Failed"})

        return org.invite(
            invitee,
            send_email=True,
            request=request,
        )


class AdminActionsSerializer(rfs.Serializer):
    class Meta:
        fields = ["username", "request_user_username"]

    username = rfs.CharField()
    request_user_username = rfs.CharField()

    def validate(self, data):
        username = data.get("username")
        try:
            request_user = User.objects.get(username=data.get("request_user_username"))
        except User.DoesNotExist:
            raise NotFound()

        try:
            # request_user must have a membership
            membership_request_user = request_user.membership
        except Membership.DoesNotExist:
            raise rfs.ValidationError(
                {"detail": "You are not a member of any organization."}
            )

        try:
            # user to promote/remove must be a member of request_user organization
            membership_user = membership_request_user.organization.members.get(
                user__username=username
            )
        except Membership.DoesNotExist:
            raise rfs.ValidationError(
                {"detail": "User to promote/remove is not part of your organization."}
            )

        if membership_user.is_owner:
            raise PermissionDenied(
                detail="You can't modify owner permission.", code=403
            )
        # only the owner can promote/remove the user as admin
        if not membership_request_user.is_owner:
            raise PermissionDenied(detail="You are not the owner of the org.", code=403)
        return data
