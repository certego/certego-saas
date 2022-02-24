import logging
from typing import TYPE_CHECKING

from cache_memoize import cache_memoize
from django.db import IntegrityError, models, transaction
from django.utils.functional import cached_property
from email_utils import NoTemplatesException

from certego_saas.ext.models import TimestampedModel
from certego_saas.settings import certego_apps_settings

from .invitation import Invitation
from .membership import Membership

if TYPE_CHECKING:
    from certego_saas.models import User

logger = logging.getLogger(__name__)


class Organization(TimestampedModel):
    """
    ``Organization`` model is related to ``User`` model
    through the ``Membership`` model.
    """

    # fields

    name = models.CharField(max_length=32, unique=True)
    MAX_MEMBERS = certego_apps_settings.ORGANIZATION_MAX_MEMBERS

    # properties

    @cached_property
    def owner_membership(self) -> Membership:
        return self.members.get(is_owner=True)

    @cached_property
    def owner(self) -> "User":
        return self.owner_membership.user

    @cached_property
    def members_count(self) -> int:
        return self.members.count()

    def pending_invitations(self) -> models.QuerySet:
        return (
            self.invitations.select_related("user")
            .filter(status=Invitation.Status.PENDING)
            .order_by("-created_at")
        )

    # utils

    def user_has_membership(self, user: "User") -> bool:
        return user.has_membership() and user.membership.organization_id == self.pk

    @classmethod
    @cache_memoize(60 * 60)
    def certego(cls) -> "Organization":
        org, _ = Organization.objects.get_or_create(name="certego")
        return org

    @classmethod
    def create(cls, name: str, owner: "User"):
        with transaction.atomic():
            from .membership import Membership

            org = cls.objects.create(name=name)
            membership = Membership.objects.create(
                user=owner, organization=org, is_owner=True
            )
            org.members.add(membership)
            org.save()
        return org

    def invite(
        self, user: "User", send_email: bool = False, request=None
    ) -> Invitation:
        if self.members_count >= self.MAX_MEMBERS:
            raise Invitation.MaxMemberException()
        if self.owner.pk == user.pk:
            raise Invitation.OwnerException()
        if self.user_has_membership(user):
            raise Invitation.AlreadyPresentException()
        try:
            inv: Invitation = Invitation.objects.create(user=user, organization=self)
        except IntegrityError:
            raise Invitation.AlreadyPendingException()
        if send_email and request:
            try:
                inv.email_invite(request)
            except NoTemplatesException as e:
                logger.error(f"Failed to send email invite. Error: {str(e)}")
        return inv

    def __str__(self):
        return f"Organization<{self.name}>"
