from django.contrib import admin

from .models import Notification

__all__ = ["NotificationAdmin"]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Django's ModelAdmin for ``Notification``.
    """

    list_display = (
        "id",
        "appname",
        "title",
        "body",
        "created_at",
    )
