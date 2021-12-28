from django.urls import include, path
from rest_framework import routers

from .views import NotificationViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter(trailing_slash=False)
router.register(r"notification", NotificationViewSet, basename="notification")

urlpatterns = [
    # router URLs
    path("", include(router.urls)),
]
