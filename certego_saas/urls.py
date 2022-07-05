# Patterns
from django.apps import apps
from django.urls import include, path

urlpatterns = []

if apps.is_installed("certego_saas.apps.user"):
    # certego_saas: user sub-app
    urlpatterns.append(
        path("", include("certego_saas.apps.user.urls")),
    )
