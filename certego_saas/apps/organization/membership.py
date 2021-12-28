from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from certego_saas.ext.models import TimestampedModel

from .apps import CertegoOrganizationConfig


class Membership(TimestampedModel):
    """
    Inspired by:
    https://docs.djangoproject.com/en/3.2/topics/db/models/#extra-fields-on-many-to-many-relationships
    """

    # meta

    class Meta:
        unique_together = [
            ("user", "organization"),
        ]

    # fields

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="membership",
        on_delete=models.CASCADE,
    )
    organization = models.ForeignKey(
        f"{CertegoOrganizationConfig.label}.Organization",
        related_name="members",
        on_delete=models.CASCADE,
    )
    is_owner = models.BooleanField(default=False)

    # funcs

    def __str__(self):
        member_str = "owner" if self.is_owner else "member"
        return f"Membership<{member_str},{self.user.username},{self.organization.name}>"

    # exceptions

    class ExistingMembershipException(ValidationError):
        default_detail = (
            "Invalid operation. User is already a member of some organization."
        )

    class OwnerCantLeaveException(ValidationError):
        default_detail = "Owner cannot leave the organization but can choose to delete the organization."
