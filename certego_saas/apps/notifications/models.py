from django.conf import settings
from django.db import models

from certego_saas.ext.models import AppSpecificModel, TimestampedModel

__all__ = [
    "Notification",
]


class Notification(TimestampedModel, AppSpecificModel):
    """
    ``Notification`` model.
    """

    # fields

    title = models.CharField(max_length=128, null=False, blank=False)
    body = models.TextField()
    read_by_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="notifications_read",
        help_text="To store which users have read a particular notification.",
        blank=True,
    )
    for_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notifications",
        help_text="If the field is empty, the notification is for everyone; otherwise only for the specified user",
        null=True,
        on_delete=models.CASCADE,
        blank=True,
    )

    def is_read_by_user(self, user) -> bool:
        return self.read_by_users.filter(pk=user.pk).exists()

    def is_for_user(self, user) -> bool:
        return self.for_user is None or self.for_user.pk == user.pk
