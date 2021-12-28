from rest_framework import serializers as rfs
from rest_flex_fields.serializers import FlexFieldsModelSerializer

from .models import User

__all__ = [
    "UserSerializer",
    "UserAccessSerializer",
]


class UserSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
        )

    full_name = rfs.CharField(source="get_full_name")


class UserAccessSerializer(rfs.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "full_name",
            "email",
        )

    full_name = rfs.CharField(source="get_full_name")
