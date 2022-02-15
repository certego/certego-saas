from django.core.cache import cache
from django.test import tag
from durin.models import AuthToken, Client
from rest_framework.reverse import reverse

from certego_saas.settings import certego_apps_settings

from ... import CustomTestCase, User

login_uri = reverse("auth_login")
logout_uri = reverse("auth_logout")


@tag("apps", "auth")
class TestAuth(CustomTestCase):
    def setUp(self):
        # test data
        self.testregisteruser = {
            "email": "testregisteruser@test.com",
            "username": "testregisteruser",
            "first_name": "testregisteruser",
            "last_name": "testregisteruser",
            "password": "testregisteruser",
            "profile": {
                "company_name": "Certego",
                "company_role": "dragonfly test",
                "twitter_handle": "@fake",
                "discover_from": "other",
            },
        }
        self.creds = {
            "username": "john.doe",
            "password": "averystrongpassword",
        }
        self.email = "john.doe@example.com"
        self.user = User.objects.create_user(
            self.creds["username"], self.email, self.creds["password"]
        )
        return super().setUp()

    def tearDown(self):
        # cache clear (for throttling)
        cache.clear()
        # db clean
        AuthToken.objects.all().delete()
        Client.objects.all().delete()
        return super().tearDown()

    # test cases

    def test_login_200(self):
        self.assertEqual(AuthToken.objects.count(), 0)

        response = self.client.post(login_uri, self.creds, format="json")
        msg = (response, "response data should be null but response should set cookie")

        self.assertEqual(response.status_code, 200, msg=msg)
        self.assertIn(
            certego_apps_settings.AUTH_TOKEN_COOKIE_NAME, response.cookies, msg=msg
        )

        self.assertEqual(AuthToken.objects.count(), 1)

    def test_logout_tokenauth_204(self):
        self.assertEqual(AuthToken.objects.count(), 0)

        token = AuthToken.objects.create(
            user=self.user,
            client=Client.objects.create(name="test_logout_tokenauth_204"),
        )
        self.assertEqual(AuthToken.objects.count(), 1)

        self.client.credentials(HTTP_AUTHORIZATION=("Token %s" % token.token))
        response = self.client.post(logout_uri)

        self.assertEqual(response.status_code, 204, msg=(response))
        self.assertEqual(
            AuthToken.objects.count(), 0, "other tokens should remain after logout"
        )

    def test_logout_cookieauth_204(self):
        self.assertEqual(AuthToken.objects.count(), 0)

        token = AuthToken.objects.create(
            user=self.user,
            client=Client.objects.create(name="test_logout_cookieauth_204"),
        )
        self.assertEqual(AuthToken.objects.count(), 1)
        self.client.cookies[certego_apps_settings.AUTH_TOKEN_COOKIE_NAME] = token.token
        response = self.client.post(logout_uri)

        self.assertEqual(response.status_code, 204, msg=(response))
        self.assertEqual(
            AuthToken.objects.count(), 0, "other tokens should remain after logout"
        )

    def test_logout_no_auth_401(self):
        response = self.client.post(logout_uri)

        self.assertEqual(response.status_code, 401, msg=(response))
