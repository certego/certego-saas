from rest_flex_fields.serializers import FlexFieldsModelSerializer
from rest_framework import serializers as rfs

from .models import User

__all__ = [
    "UserSerializer",
    "UserAccessSerializer",
]


class UserSerializer(FlexFieldsModelSerializer):
    """
    Reusable serializer for :class:`~.models.User` model.
    """

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
        )


class UserAccessSerializer(rfs.ModelSerializer):
    """
    Used by :class:`~.views.UserAccessView`.

    Ideally, this serializer should be extended inside your
    service's source code adding user relevant information
    and then point to it with the
    ``USER_ACCESS_SERIALIZER`` settings variable.
    """

    class Meta:
        model = User
        fields = ("user",)

    user = rfs.SerializerMethodField()

    def get_user(self, obj: User) -> dict:
        return UserSerializer(instance=obj).data
