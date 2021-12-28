from django.conf import settings
from django.db import models

from certego_saas.ext.models import AppSpecificModel, TimestampedModel


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
