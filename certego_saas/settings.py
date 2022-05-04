import os

import stripe
from django.conf import settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings

# placeholder for later
get_secret = os.environ.get

TEST_RUNNER = "tests.timed_runner.TimedRunner"
# stripe-python
STRIPE_LIVE_MODE = (
    settings.PUBLIC_DEPLOYMENT and not settings.STAGE_CI and not settings.DEBUG
)
stripe.api_key = str(
    get_secret("STRIPE_LIVE_SECRET_KEY", None)
    if STRIPE_LIVE_MODE
    else get_secret("STRIPE_TEST_SECRET_KEY", None)
)

USER_SETTINGS = getattr(settings, "CERTEGO_SAAS", None)

DEFAULTS = {
    # app settings
    "AUTH_TOKEN_COOKIE_NAME": "CERTEGO_SAAS_AUTH_TOKEN",
    "AUTH_COOKIE_HTTPONLY": True,
    "AUTH_COOKIE_SAMESITE": "Strict",
    "AUTH_COOKIE_DOMAIN": None,
    "FILTER_NOTIFICATIONS_VIEW_FOR_CURRENTAPP": True,
    "USER_ACCESS_SERIALIZER": "certego_saas.user.serializers.UserAccessSerializer",
    "ORGANIZATION_MAX_MEMBERS": 3,
    # app info
    "HOST_URI": settings.HOST_URI,
    "HOST_NAME": settings.HOST_NAME,
    # third party keys
    "SLACK_TOKEN": get_secret("SLACK_TOKEN", None),
    "SLACK_CHANNEL": get_secret("SLACK_CHANNEL", None),
    "TWITTER_CONSUMER_KEY": get_secret("TWITTER_CONSUMER_KEY", None),
    "TWITTER_CONSUMER_SECRET": get_secret("TWITTER_CONSUMER_SECRET", None),
    "TWITTER_TOKEN_KEY": get_secret("TWITTER_TOKEN_KEY", None),
    "TWITTER_TOKEN_SECRET": get_secret("TWITTER_TOKEN_SECRET", None),
    "STRIPE_LIVE_MODE": STRIPE_LIVE_MODE,
    "STRIPE_WEBHOOK_SIGNING_KEY": get_secret("STRIPE_WEBHOOK_SIGNING_KEY", None),
}

IMPORT_STRINGS = ["USER_ACCESS_SERIALIZER"]

certego_apps_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)  # type: ignore


def _reload_settings(*args, **kwargs):
    global certego_apps_settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == "CERTEGO_SAAS":
        certego_apps_settings = APISettings(value, DEFAULTS, IMPORT_STRINGS)


setting_changed.connect(_reload_settings)
