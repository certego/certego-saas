from typing import Tuple

from rest_framework.test import APIClient

from certego_saas.apps.payments.consts import (
    TEST_ADMIN_CUSTOMER_ID,
    TEST_ADMIN_DF_SUBSCRIPTION_ID,
)
from certego_saas.models import Customer, Subscription, User

# flake8: noqa
from ... import CustomTestCase


def setup() -> Tuple[APIClient, User]:
    user, _ = User.objects.get_or_create(
        username="stripetestuser",
        email="cti@certego.net",
    )
    customer, _ = Customer.objects.get_or_create(
        customer_id=TEST_ADMIN_CUSTOMER_ID,
        user=user,
    )
    subscription, _ = Subscription.objects.get_or_create(
        subscription_id=TEST_ADMIN_DF_SUBSCRIPTION_ID,
        appname=Subscription.AppChoices.DRAGONFLY,
        customer=customer,
    )
    user.refresh_from_db()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def setup_new_customer() -> Tuple[APIClient, User]:
    user, _ = User.objects.get_or_create(
        username="testpayments", email="testpayments@test.com"
    )
    user.get_or_create_customer()
    user.refresh_from_db()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user
