from django.urls import include, path
from rest_framework import routers

from .views import InvitationViewSet, OrganizationViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.SimpleRouter(trailing_slash=False)
router.register(r"organization", OrganizationViewSet, basename="user_organization")
router.register(r"invitations", InvitationViewSet, basename="user_invitations")

urlpatterns = [
    # router URLs
    path("", include(router.urls)),
]
