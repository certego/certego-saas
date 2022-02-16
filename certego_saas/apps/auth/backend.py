from durin import auth
from rest_framework.request import Request

from certego_saas.settings import certego_apps_settings

TOKEN_COOKIE_NAME = certego_apps_settings.AUTH_TOKEN_COOKIE_NAME


class CookieTokenAuthentication(auth.TokenAuthentication):
    def authenticate(self, request: Request):
        if TOKEN_COOKIE_NAME in request.COOKIES:
            token_bytes = request.COOKIES[TOKEN_COOKIE_NAME].encode()
            return self.authenticate_credentials(token_bytes)
        return super().authenticate(request)


class CachedCookieTokenAuthentication(auth.CachedTokenAuthentication):
    def authenticate(self, request: Request):
        if TOKEN_COOKIE_NAME in request.COOKIES:
            token_bytes = request.COOKIES[TOKEN_COOKIE_NAME].encode()
            return self.authenticate_credentials(token_bytes)
        return super().authenticate(request)
