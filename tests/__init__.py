from typing import Tuple

from rest_framework.test import APIClient, APITestCase

from certego_saas.models import User


def setup() -> Tuple[APIClient, User]:
    user = User.certego()
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


def setup_custom_user(user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class CustomTestCase(APITestCase):
    pass
