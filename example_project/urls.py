from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(url="admin/", permanent=False)),
    path("admin/", admin.site.urls, name="admin"),
    # certego_saas:
    # default apps (user),
    path("api/", include("certego_saas.urls")),
    # notifications sub-app
    path("api/", include("certego_saas.apps.notifications.urls")),
    # organization sub-app
    path("api/me/", include("certego_saas.apps.organization.urls")),
]
