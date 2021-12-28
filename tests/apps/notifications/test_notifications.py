from django.test import tag
from rest_framework.reverse import reverse

from certego_saas.apps.notifications.models import Notification

from ... import CustomTestCase, setup

notification_list_uri = reverse("notification-list")


@tag("apps", "notifications")
class TestNotifications(CustomTestCase):
    def setUp(self) -> None:
        # prune current data
        Notification.objects.all().delete()
        # setup client and user
        self.client, self.user = setup()
        # create test notifs
        self.notif_1 = Notification.objects.create(
            title="Test #1", body="Test #1", appname=Notification.AppChoices.CURRENTAPP
        )
        self.notif_2 = Notification.objects.create(
            title="Test #2", body="Test #2", appname=Notification.AppChoices.CURRENTAPP
        )
        self.notif_2.read_by_users.add(self.user)
        return super().setUp()

    def test_list_200(self):
        # base asserts
        self.assertEqual(2, Notification.objects.all().count())

        # 1. Without filter
        response = self.client.get(notification_list_uri)
        content = response.json()
        msg = (content, "All notifications")

        self.assertEqual(200, response.status_code, msg=msg)
        self.assertEqual(2, content["count"], msg=msg)

        # 2. read=false
        response = self.client.get(f"{notification_list_uri}?read=false")
        content = response.json()
        msg = (content, "Only unread notifications")

        self.assertEqual(200, response.status_code, msg=msg)
        self.assertEqual(1, content["count"], msg=msg)
        self.assertEqual(False, any(n["read"] for n in content["results"]), msg=msg)

        # 1. read=true
        response = self.client.get(f"{notification_list_uri}?read=true")
        content = response.json()
        msg = (content, "Only read notifications")

        self.assertEqual(200, response.status_code, msg=msg)
        self.assertEqual(1, content["count"], msg=msg)
        self.assertEqual(True, any(n["read"] for n in content["results"]), msg=msg)

    def test_mark_as_read_204(self):
        # dummy notif object
        testnotif = Notification.objects.create(
            title="test_mark_as_read_204", appname=Notification.AppChoices.CURRENTAPP
        )
        # base assertions
        self.assertFalse(
            testnotif.read_by_users.filter(pk__in=[self.user.pk]).exists(),
            msg="Currently unread for self.user",
        )

        # api call
        uri = reverse("notification-mark_as_read", args=[testnotif.pk])
        response = self.client.post(uri)

        self.assertEqual(204, response.status_code)
        self.assertTrue(
            testnotif.read_by_users.filter(pk__in=[self.user.pk]).exists(),
            msg="Should now be read for self.user",
        )

        # cleanup
        testnotif.delete()
