import logging

import email_utils
from django.conf import settings
from django.db import models, transaction
from rest_framework.exceptions import ValidationError

from certego_saas.ext.models import TimestampedModel

from .apps import CertegoOrganizationConfig
from .membership import Membership

logger = logging.getLogger(__name__)


__all__ = ["Invitation"]


class Status:
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"


class Invitation(TimestampedModel):
    # Meta
    Status = Status

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                fields=[
                    "user",
                    "organization",
                ],
                condition=models.Q(status=Status.PENDING),
                name="user_org_pair_single_pending_invite",
            )
        ]

    # fields

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="invitations"
    )
    organization = models.ForeignKey(
        f"{CertegoOrganizationConfig.label}.Organization",
        related_name="invitations",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=12,
        choices=[
            (Status.PENDING, Status.PENDING),
            (Status.ACCEPTED, Status.ACCEPTED),
            (Status.DECLINED, Status.DECLINED),
        ],
        default=Status.PENDING,
    )

    # exceptions

    class OwnerException(ValidationError):
        default_detail = "Cannot create invitation for organization owner."

    class MaxMemberException(ValidationError):
        default_detail = "Organization reached maximum number of members."

    class AlreadyPresentException(ValidationError):
        default_detail = "Invite failed. User is already part of the organization."

    class AlreadyPendingException(ValidationError):
        default_detail = "A similar invite for the user is already pending."

    class PreviouslyDeclinedException(ValidationError):
        default_detail = "Invitation was previously declined."

    class PreviouslyAcceptedException(ValidationError):
        default_detail = "Invitation was previously accepted."

    # funcs

    def is_pending(self) -> bool:
        return self.status == self.Status.PENDING

    def accept(self) -> None:
        if self.organization.members_count >= self.organization.MAX_MEMBERS:
            raise self.MaxMemberException()
        if self.user.has_membership():
            raise Membership.ExistingMembershipException()
        if self.status == self.Status.DECLINED:
            raise self.PreviouslyDeclinedException()
        if self.status == self.Status.ACCEPTED:
            raise self.PreviouslyAcceptedException()

        with transaction.atomic():
            self.user.membership = Membership.objects.create(
                user=self.user, organization=self.organization
            )
            self.status = self.Status.ACCEPTED
            self.user.save()
            self.save()

    def decline(self) -> None:
        if self.status == self.Status.ACCEPTED:
            raise self.PreviouslyAcceptedException()
        if self.status == self.Status.DECLINED:
            raise self.PreviouslyDeclinedException()

        self.status = self.Status.DECLINED
        self.save()

    def email_invite(self, request) -> None:
        email_utils.send_email(
            context={
                "username": self.user.username,
                "organization_name": self.organization.name,
                "organization_owner_username": self.organization.owner.get_username(),
                "invitation_uri": request.build_absolute_uri("/"),
                "host_uri": request.build_absolute_uri("/me/invitations"),
            },
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            subject=f"Certego - Invitation to join {self.organization.name} organization",
            template_name="certego_saas/emails/org-invitation",
        )

    def __str__(self):
        return f"Invitation<{self.status}>"
