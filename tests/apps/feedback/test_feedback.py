from django.test import tag
from rest_framework.reverse import reverse

from certego_saas.apps.feedback.models import UserFeedback

from ... import CustomTestCase, setup

user_feedback_uri = reverse("user_feedback-list")


@tag("apps", "feedback")
class TestFeedback(CustomTestCase):
    def setUp(self) -> None:
        UserFeedback.objects.all().delete()
        self.client, self.user = setup()
        return super().setUp()

    def test_create_feedback_201(self):
        self.assertEqual(UserFeedback.objects.count(), 0)

        req_body = {
            "category": "BUG_REPORT",
            "message": "Blah blah",
        }
        response = self.client.post(user_feedback_uri, data=req_body)
        content = response.json()

        self.assertEqual(201, response.status_code, content)
        self.assertEqual(UserFeedback.objects.count(), 1)
