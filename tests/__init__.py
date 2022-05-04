import logging
from typing import Tuple

from rest_framework.test import APIClient, APITestCase

from certego_saas.models import User
from tests.no_logs_test_case import NoLogsTestCase
from tests.timed_test_case import TimedTestCase, TimedTextTestRunner


def setup() -> Tuple[APIClient, User]:
    user = User.certego()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def setup_custom_user(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class CustomTestCase(APITestCase, NoLogsTestCase, TimedTestCase):
    test_runner = TimedTextTestRunner

    def setUp(self) -> None:
        self.max_logging_level = logging.CRITICAL

    def assertNoLogs(self, logger=None, level=None):
        if not logger:
            logger = logging.getLogger()
        return NoLogsTestCase.assertNoLogs(self, logger, level)
