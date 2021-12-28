from django.test import tag

from . import CustomTestCase, setup, setup_new_customer


@tag("apps", "payments")
class TestPayments(CustomTestCase):
    def test_create_customer(self):
        client, user = setup()
        self.assertTrue(user.has_customer(), "customer should already exist")

    def test_create_new_customer(self):
        client, user = setup_new_customer()
        self.assertTrue(user.has_customer(), "new customer should be created")

        user.customer._delete_customer()
