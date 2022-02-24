from typing import List, Tuple

import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache as default_cache
from django.db import models, transaction
from django.utils.functional import cached_property

from certego_saas.ext.models import AppChoices, AppSpecificModel

from .apps import CertegoPaymentsConfig
from .cache import cache_memoize
from .exceptions import CustomerWithoutSubscription
from .utils import get_default_product

__all__ = [
    "AppChoices",
    "Customer",
    "Subscription",
]


class Customer(models.Model):
    """
    A wrapper class over ``stripe-python`` SDK
    combined with django's ``User`` model
    that provides utilities for retrieving customer and their subscription details.
    """

    # fields

    customer_id = models.CharField(max_length=64, primary_key=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer"
    )

    # constants

    CustomerWithoutSubscription = CustomerWithoutSubscription

    # subscription info

    @cached_property
    def currentapp_subscription(self) -> "Subscription":
        try:
            return self.subscriptions.get(appname=AppChoices.CURRENTAPP)
        except Subscription.DoesNotExist:
            return Subscription(customer=self, appname=AppChoices.CURRENTAPP)

    @cached_property
    def dragonfly_subscription(self) -> "Subscription":
        try:
            return self.subscriptions.get(appname=AppChoices.DRAGONFLY)
        except Subscription.DoesNotExist:
            return Subscription(customer=self, appname=AppChoices.DRAGONFLY)

    @cached_property
    def intelowl_subscription(self) -> "Subscription":
        try:
            return self.subscriptions.get(appname=AppChoices.INTELOWL)
        except Subscription.DoesNotExist:
            return Subscription(customer=self, appname=AppChoices.INTELOWL)

    # stripe API: utility methods

    @cache_memoize(60 * 15)
    def create_checkout_session(
        self, price_id, success_url, cancel_url
    ) -> stripe.checkout.Session:
        """
        uses :meth:``stripe.checkout.Session.create``.

        * `Stripe Checkout Docs <https://stripe.com/private_docs/payments/checkout>`__
        """
        return stripe.checkout.Session.create(
            customer=self.customer_id,
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
        )

    @cache_memoize(60 * 15)
    def create_billing_portal_session(
        self, return_url
    ) -> stripe.billing_portal.Session:
        """
        uses :meth:``stripe.billing_portal.Session.create``.

        * `Stripe Billing Portal settings <https://dashboard.stripe.com/test/settings/billing/portal>`__
        """
        return stripe.billing_portal.Session.create(
            customer=self.customer_id, return_url=return_url
        )

    # stripe API: fetch methods

    @cache_memoize(60 * 60 * 12)
    def get_stripe_customer(self) -> stripe.Customer:
        """
        Returns instance of :class:`stripe.Customer` for user.

        * (uses :meth:``stripe.Customer.retrieve()``
        """
        return stripe.Customer.retrieve(self.customer_id)

    # stripe API: mutation methods

    @classmethod
    @transaction.atomic
    def _create_customer(cls, user_id) -> Tuple["Customer", bool]:
        """
        Create customer on stripe for this user.
        For internal use only.
        """
        created = False
        user = get_user_model().objects.select_for_update().get(pk=user_id)

        # basic check
        try:
            return user.customer, created
        except cls.DoesNotExist:
            pass

        # create new customer in stripe DB
        stripe_customer = stripe.Customer.create(
            email=user.email,
            name=user.get_full_name(),
            metadata={
                "user_id": user.id,
                "username": user.get_username(),
                "host": default_cache.get("current_site", None)
                # "organization": user.organization.name,
            },
        )

        # create new Customer instance
        customer = cls.objects.create(customer_id=stripe_customer.id, user=user)
        created = True

        return customer, created

    def _delete_customer(self) -> bool:
        """
        **WARNING: DANGEROUS OPERATION**

        Deletes customer on stripe and from DB for this user/customer.
        For usage in tests only.
        """

        # delete customer on stripe DB
        deleted = stripe.Customer.delete(self.customer_id).deleted

        # delete customer instance
        self.delete()

        return deleted

    # repr methods

    def __str__(self) -> str:
        return f"<customer:{self.customer_id},user:{self.user_id}>"


class Subscription(AppSpecificModel):
    """
    Each ``Customer`` can have maximum ``len(AppChoices)`` number of
    related ``Subscription`` objects; one subscription for
    each app name (i.e. DRAGONFLY, INTELOWL, etc.).
    """

    # fields

    subscription_id = models.CharField(max_length=64, primary_key=True)
    customer = models.ForeignKey(
        f"{CertegoPaymentsConfig.label}.Customer",
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )

    # meta

    class Meta:
        unique_together = [
            ("customer", "appname"),
        ]

    # useful properties

    @property
    def product_name(self) -> str:
        try:
            return str(self.subscribed_product().name)
        except CustomerWithoutSubscription:
            default_product = get_default_product()
            return default_product["name"]

    @property
    def priority(self) -> bool:
        """
        ``metadata.priority``
        """
        priority = False
        try:
            priority = self.subscribed_product().metadata.priority
        except CustomerWithoutSubscription:
            default_product = get_default_product()
            priority = default_product["metadata"]["priority"]
        finally:
            priority = priority == "True"
        return priority

    @property
    def monthly_submissions_limit(self) -> int:
        """
        ``metadata.max_submissions``
        """
        try:
            max_submissions = self.subscribed_product().metadata.max_submissions
        except CustomerWithoutSubscription:
            default_product = get_default_product()
            max_submissions = default_product["metadata"]["max_submissions"]

        return int(max_submissions)

    @property
    def can_submit_private(self) -> bool:
        """
        ``metadata.submission_type == "private"``
        """
        try:
            submission_type = self.subscribed_product().metadata.submission_type
        except CustomerWithoutSubscription:
            default_product = get_default_product()
            submission_type = default_product["metadata"]["submission_type"]

        return submission_type == "private"

    @property
    def concurrent_profiles(self) -> int:
        """
        ``metadata.max_submissions``
        """
        try:
            concurrent_profiles = self.subscribed_product().metadata.concurrent_profiles
        except CustomerWithoutSubscription:
            default_product = get_default_product()
            concurrent_profiles = default_product["metadata"]["concurrent_profiles"]

        return int(concurrent_profiles)

    # utility methods

    def has_active_subscription(self) -> bool:
        try:
            status = self.get_subscription().status
            return status == "active"
        except CustomerWithoutSubscription:
            return False

    def active_subscription(self) -> dict:
        active_sub = self.get_subscription(expand=["plan.product"])
        product = active_sub.plan.product
        return {
            "appname": self.appname,
            "status": active_sub.status,
            "current_period_start": active_sub.current_period_start,
            "current_period_end": active_sub.current_period_end,
            "days_until_due": active_sub.days_until_due,
            "start_date": active_sub.start_date,
            "created": active_sub.created,
            "ended_at": active_sub.ended_at,
            "cancel_at": active_sub.cancel_at,
            "cancel_at_period_end": active_sub.cancel_at_period_end,
            "canceled_at": active_sub.canceled_at,
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "metadata": product.metadata,
                "currency": active_sub.plan.currency,
                "unit_amount": active_sub.plan.amount,
            },
            "invoices": self.get_invoices(),
        }

    def subscribed_product(self) -> stripe.Product:
        """
        Product details for the active subscription.
        """
        subscription = self.get_subscription(expand=["plan.product"])
        return subscription.plan.product

    # stripe API: fetch methods

    @cache_memoize(60 * 60 * 12)
    def get_subscription(self, expand=None) -> stripe.Subscription:
        """
        Returns customer's active subscription.

        * (uses :meth:``stripe.Subscription.retrieve()``
        """
        expand = expand or []
        if not self.subscription_id:
            raise CustomerWithoutSubscription(appname=self.appname)
        subscription = stripe.Subscription.retrieve(self.subscription_id, expand=expand)
        return subscription

    @cache_memoize(60 * 60 * 12)
    def get_invoices(self) -> List[stripe.Invoice]:
        invoices = stripe.Invoice.list(subscription=self.subscription_id).data
        # sort in descending order of "created"
        return sorted(invoices, key=lambda o: o.created, reverse=True)

    def get_latest_invoice(self) -> stripe.Invoice:
        return self.get_subscription(expand=["latest_invoice"]).latest_invoice

    # repr methods

    def __str__(self) -> str:
        return f"<app:{self.appname},sub:{self.subscription_id}>"
