import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from django_user_agents.utils import get_user_agent
from durin import views as durin_views
from durin.models import Client

from certego_saas.settings import certego_apps_settings


logger = logging.getLogger(__name__)

__all__ = [
    "LoginView",
    "LogoutView",
    "APIAccessTokenView",
    "TokenSessionsViewSet",
]


class LoginView(durin_views.LoginView):
    def get_client_obj(self, request) -> Client:
        client_name = get_user_agent(request)
        client, _ = Client.objects.get_or_create(name=client_name)
        return client

    def post(self, request, *args, **kwargs) -> Response:
        request.user = self.validate_and_return_user(request)
        logger.info(f"LoginView: received request from '{request.user.username}'.")
        client = self.get_client_obj(request)
        token_obj = self.get_token_obj(request, client)
        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(
            key=certego_apps_settings.AUTH_TOKEN_COOKIE_NAME,
            value=token_obj.token,
            expires=token_obj.expiry,
            secure=False if settings.STAGE_CI or settings.DEBUG else True,
            httponly=True,
            samesite="Strict",
            # secure=True,
        )
        return response


class LogoutView(durin_views.LogoutView):
    def post(self, request, *args, **kwargs) -> Response:
        super().post(request, *args, **kwargs)
        uname = request.user.username
        logger.info(f"LogoutView: request from '{uname}''.")
        response = super(LogoutView, self).post(request, *args, **kwargs)
        response.delete_cookie(
            key=certego_apps_settings.AUTH_TOKEN_COOKIE_NAME,
            samesite="Strict",
        )
        return response


APIAccessTokenView = durin_views.APIAccessTokenView
TokenSessionsViewSet = durin_views.TokenSessionsViewSet
