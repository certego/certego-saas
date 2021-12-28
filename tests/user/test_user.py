from django.test import tag
from rest_framework.reverse import reverse

from certego_saas.settings import certego_apps_settings

from .. import CustomTestCase, setup

user_access_uri = reverse("user_access")
UserAccessSerializer = certego_apps_settings.USER_ACCESS_SERIALIZER  # import string


@tag("api", "user")
class TestUserViews(CustomTestCase):
    def setUp(self) -> None:
        self.client, self.user = setup()
        return super().setUp()

    def test_user_access_200(self):
        response = self.client.get(user_access_uri)
        content = response.json()
        msg = (response, content)

        self.assertEqual(200, response.status_code, content)
        for field in UserAccessSerializer.Meta.fields:
            self.assertIn(field, content, msg=msg)
