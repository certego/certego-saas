from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.functional import classproperty

from .managers import AppSpecificModelManager, ToggleableModelManager


class AppChoices(models.TextChoices):
    ACCOUNTS = "ACCOUNTS"
    DRAGONFLY = "DRAGONFLY"
    INTELOWL = "INTELOWL"

    @classproperty
    def CURRENTAPP(cls) -> str:
        try:
            return cls[settings.HOST_NAME.upper()]  # type: ignore
        except KeyError:
            raise ImproperlyConfigured(f"Incorrect HOST_NAME: {settings.HOST_NAME} set")


class TimestampedModel(models.Model):
    """
    Adds a ``created_at`` timestamp field with ``auto_now_add=True``.
    """

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

        # By default, any model that inherits from `TimestampedModel` should
        # be ordered in reverse-chronological order. We can override this on a
        # per-model basis as needed, but reverse-chronological is a good
        # default ordering for most models.
        ordering = ["-created_at"]


class ToggleableModel(models.Model):
    """
    Provides a ``enabled`` field and prevents deletion.
    """

    enabled = models.BooleanField(default=True)

    objects = ToggleableModelManager()

    class Meta:
        abstract = True

    def disable(self):
        if self.enabled:
            self.enabled = False
            self.save(update_fields=["enabled"])

    def enable(self):
        if not self.enabled:
            self.enabled = True
            self.save(update_fields=["enabled"])


class AppSpecificModel(models.Model):
    """
    Adds a ``appname`` choice field (``AppChoices``) and
    provides ``get_currentapp`` and ``filter_currentapp`` methods to the queryset and manager.
    """

    appname = models.CharField(
        max_length=32,
        choices=AppChoices.choices,
        null=False,
    )

    objects = AppSpecificModelManager()

    AppChoices = AppChoices

    class Meta:
        abstract = True
