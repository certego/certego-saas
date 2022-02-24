# flake8: noqa
from django.apps import apps

from .user.models import User

__all__ = ["User"]

if apps.is_installed("certego_saas.apps.organization"):
    # import these models only if organization app is installed,
    # otherwise it will throw an error
    from .apps.organization.models import Organization

    __all__ += ["Organization"]


if apps.is_installed("certego_saas.apps.payments"):
    # import these models only if payments app is installed,
    # otherwise it will throw an error
    from .apps.payments.models import Customer, Subscription

    __all__ += ["Customer", "Subscription"]
