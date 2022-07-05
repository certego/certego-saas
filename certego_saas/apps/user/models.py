from typing import List, Optional, Tuple, Union

from cache_memoize import cache_memoize
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.db import models
from django.dispatch import receiver

from certego_saas.apps.organization.models import Membership, Organization

__all__ = [
    "User",
]


class AbstractUser(DjangoAbstractUser):
    """Custom User Model

    * ref:
    https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
    """

    REQUIRED_FIELDS = ["email", "first_name", "last_name"]
    approved = models.BooleanField(
        default=None,
        null=True,
        help_text="True if accepted, False if declined, None if noop.",
    )

    # meta

    class Meta:
        abstract = True
        app_label = "certego_saas"

    # utils

    @property
    def full_name(self) -> str:
        return self.get_full_name()

    @classmethod
    @cache_memoize(60 * 60)
    def certego(cls) -> "User":
        user, _ = User.objects.get_or_create(username="certego")
        if not user.has_membership():
            certego_org = Organization.certego()
            user.membership = Membership.objects.create(
                user=user,
                organization=certego_org,
                is_owner=True,
            )
            user.membership.save()
        return user

    # organization

    def same_organization(self, other: Union["User", Organization]) -> bool:
        if not self.has_membership():
            return False
        if isinstance(other, User):
            if not other.has_membership():
                return False
            return self.membership.organization == other.membership.organization  # type: ignore
        if isinstance(other, Organization):
            return self.membership.organization == other  # type: ignore
        raise RuntimeError(f"Other is not User or Organization, but {type(other)}")

    def has_membership(self) -> bool:
        return hasattr(self, "membership") and self.membership is not None  # type: ignore

    # ORM

    @property
    def is_email_verified(self) -> Optional[bool]:
        """
        True if verified, False if not, None if LDAP/manually created user
        """
        verified_cumulative = self.email_addresses.values_list("is_verified", flat=True)  # type: ignore
        if len(verified_cumulative):
            return any(verified_cumulative)
        return None  # case: LDAP/manually created user


if apps.is_installed("certego_saas.apps.payments"):
    from certego_saas.apps.payments.models import Customer, Subscription

    class User(AbstractUser):
        class Meta:
            app_label = "certego_saas"

        def has_customer(self) -> bool:
            return hasattr(self, "customer") and self.customer is not None

        def get_or_create_customer(self) -> Tuple[Customer, bool]:
            if self.has_customer():
                return self.customer, False
            return Customer._create_customer(user_id=self.pk)

        # df specific

        @classmethod
        @property
        def INTEGRATIONS(cls) -> List["User"]:
            """
            We have to update this with the integration users
            """
            return [
                User.objects.get_or_create(
                    username="abuse-ch", email="dragonfly@abuse.ch"
                )[
                    0
                ],  # malware bazaar
            ]

    @receiver(models.signals.post_save, sender=User)
    def post_save_user_handler(sender, instance: User, created: bool, **kwargs):
        """
        Create corresponding ``Customer`` instance.
        """
        from certego_saas.apps.payments.consts import (
            TEST_ADMIN_CUSTOMER_ID,
            TEST_ADMIN_DF_SUBSCRIPTION_ID,
        )

        if (
            (not created)
            or (settings.STAGE_CI)
            or (
                (not instance.is_active)
                or instance.is_anonymous
                or instance.username == "certego"  # certego user
                or instance.username == "intelowl"  # intelowl user
            )
        ):
            return

        if (not settings.PUBLIC_DEPLOYMENT) and (
            instance.username == "admin" and instance.is_superuser
        ):
            customer, _ = Customer.objects.get_or_create(
                customer_id=TEST_ADMIN_CUSTOMER_ID,
                user=instance,
            )
            subscription, _ = Subscription.objects.get_or_create(
                subscription_id=TEST_ADMIN_DF_SUBSCRIPTION_ID,
                appname=Subscription.AppChoices.DRAGONFLY,
                customer=customer,
            )
            return

        customer, _ = instance.get_or_create_customer()

else:

    class User(AbstractUser):  # type: ignore
        class Meta:
            app_label = "certego_saas"
