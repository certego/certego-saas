from django.urls import include, path
from rest_framework import routers

from .views import (
    LoginView,
    LogoutView,
    APIAccessTokenView,
    TokenSessionsViewSet,
)

router = routers.SimpleRouter(trailing_slash=False)
router.register(r"sessions", TokenSessionsViewSet, basename="auth_tokensessions")

urlpatterns = [
    # durin + Custom Auth APIs
    path("login", LoginView.as_view(), name="auth_login"),
    path("logout", LogoutView.as_view(), name="auth_logout"),
    # durin + sessions management related URLs
    path("apiaccess", APIAccessTokenView.as_view(), name="auth_apiaccess"),
    path("", include(router.urls)),
]
