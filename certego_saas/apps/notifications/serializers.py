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
        read = getattr(obj, "read", None)
        if read is not None:
            return read
        # else query again
        rqst_user = self.context["request"].user
        return obj.read_by_users.filter(pk=rqst_user.pk).exists()
