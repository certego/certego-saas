from rest_framework import serializers as rfs

from .models import Notification


class NotificationSerializer(rfs.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "title",
            "body",
            "created_at",
            "read",
        )

    read = rfs.SerializerMethodField()

    def get_read(self, obj: Notification) -> bool:
        # `read` property may already be present inside `obj`
        # see filters.py L15 and L19
        read = getattr(obj, "read", None)
        if read is not None:
            return read
        # if not present, query again
        rqst_user = self.context["request"].user
        return obj.is_read_by_user(rqst_user)
