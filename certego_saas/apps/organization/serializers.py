from rest_flex_fields.serializers import FlexFieldsModelSerializer
from rest_framework import serializers as rfs

from certego_saas.user.models import User
from certego_saas.user.serializers import UserSerializer

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
        fields = ["username", "full_name", "joined"]

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
            raise rfs.ValidationError({"detail": "Failed. No such user found."})

        return org.invite(
            invitee,
            send_email=True,
            request=request,
        )
