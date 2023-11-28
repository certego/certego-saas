from django.db import transaction
from django.test import tag
from rest_framework.reverse import reverse

from certego_saas.apps.organization.models import Invitation, Membership, Organization
from certego_saas.settings import certego_apps_settings

from ... import CustomTestCase, User

org_uri = reverse("user_organization-list")
org_leave_uri = reverse("user_organization-leave")
org_invite_uri = reverse("user_organization-invite")
org_remove_member_uri = reverse("user_organization-remove-member")
org_remove_admin_uri = reverse("user_organization-remove-admin")
org_promote_admin_uri = reverse("user_organization-promote-admin")


@tag("apps", "organization")
class TestOrganization(CustomTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # change org user limit
        Organization.MAX_MEMBERS = 5
        # create test users
        cls.user_owner_org_1: User = User.objects.get_or_create(
            username="test_user_owner_org_1"
        )[0]
        cls.user_admin_org_1: User = User.objects.get_or_create(
            username="test_user_admin_org_1"
        )[0]
        cls.user_admin2_org_1: User = User.objects.get_or_create(
            username="test_user_admin2_org_1"
        )[0]
        cls.user_common_org_1: User = User.objects.get_or_create(
            username="test_user_common_org_1"
        )[0]
        cls.user_common2_org_1: User = User.objects.get_or_create(
            username="test_user_common2_org_1"
        )[0]
        cls.user_owner_org_2: User = User.objects.get_or_create(
            username="test_user_owner_org_2"
        )[0]
        cls.user_common_org_2: User = User.objects.get_or_create(
            username="test_user_common_org_2"
        )[0]
        cls.user_no_org: User = User.objects.get_or_create(username="test_user_no_org")[
            0
        ]
        cls.user_invited: User = User.objects.get_or_create(
            username="test_user_invited"
        )[0]
        # NOTE: orgs and memberships are created in the setUp because some tests change them

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        # reset org member limit
        Organization.MAX_MEMBERS = certego_apps_settings.ORGANIZATION_MAX_MEMBERS
        # clean db
        Invitation.objects.all().delete()
        Membership.objects.all().delete()
        Organization.objects.all().delete()

    def setUp(self) -> None:
        super().setUp()
        # clean db
        Invitation.objects.all().delete()
        Membership.objects.all().delete()
        Organization.objects.all().delete()
        # create test orgs
        self.org_1: Organization = Organization.create(
            name="testorg1", owner=self.user_owner_org_1
        )
        self.org_2: Organization = Organization.create(
            name="testorg2", owner=self.user_owner_org_2
        )
        # add users to the orgs
        Membership.objects.create(
            user=self.user_admin_org_1, organization=self.org_1, is_admin=True
        )
        Membership.objects.create(
            user=self.user_admin2_org_1, organization=self.org_1, is_admin=True
        )
        Membership.objects.create(user=self.user_common_org_1, organization=self.org_1)
        Membership.objects.create(user=self.user_common2_org_1, organization=self.org_1)
        Membership.objects.create(user=self.user_common_org_2, organization=self.org_2)
        # add invite
        Invitation.objects.create(user=self.user_invited, organization=self.org_2)
        # refresh the user
        self.user_owner_org_1.refresh_from_db()
        self.user_admin_org_1.refresh_from_db()
        self.user_admin2_org_1.refresh_from_db()
        self.user_common_org_1.refresh_from_db()
        self.user_common2_org_1.refresh_from_db()
        self.user_owner_org_2.refresh_from_db()
        self.user_common_org_2.refresh_from_db()
        self.user_no_org.refresh_from_db()
        self.user_invited.refresh_from_db()

    def tearDown(self) -> None:
        super().tearDown()
        Invitation.objects.all().delete()
        Membership.objects.all().delete()
        Organization.objects.all().delete()

    def test_correct_org_creation(self):
        """User without an org can create an org"""
        self.assertEqual(2, Organization.objects.count())

        # create org
        self.client.force_authenticate(self.user_no_org)
        response = self.client.post(org_uri, {"name": "new_org"})
        self.assertEqual(201, response.status_code)
        content = response.json()
        # asserts
        self.assertEqual(3, Organization.objects.count())
        self.assertEqual("new_org", content["name"])
        self.assertEqual(1, content["members_count"])
        self.assertTrue(content["is_user_owner"])
        self.assertEqual(self.user_no_org.username, content["owner"]["username"])
        self.assertTrue(content["owner"]["is_admin"])

    def test_error_org_creation(self):
        """User in an org (owner, admin or common user) cannot create a new org while they are members."""
        # error in case the member of an org (owner, admin or common user) try to create a new org
        # owner user
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(org_uri, data={"name": "no_org"})
        content = response.json()
        self.assertIn(
            Membership.ExistingMembershipException.default_detail, content["errors"]
        )
        # admin user
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(org_uri, data={"name": "no_org"})
        content = response.json()
        self.assertIn(
            Membership.ExistingMembershipException.default_detail, content["errors"]
        )
        # common user
        self.client.force_authenticate(self.user_common_org_1)
        response = self.client.post(org_uri, data={"name": "no_org"})
        content = response.json()
        self.assertIn(
            Membership.ExistingMembershipException.default_detail, content["errors"]
        )

    def test_correct_org_deletion(self):
        """Org's owner (user_owner_org_1) can delete the org"""
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.delete(org_uri)
        self.assertEqual(204, response.status_code)

    def test_error_org_deletion(self):
        """Members of an org without owner role or user without an org cannot delete the org"""
        # admin user
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.delete(org_uri)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You do not have permission to perform this action.",
            response.json()["detail"],
        )
        # common user
        self.client.force_authenticate(self.user_common_org_1)
        response = self.client.delete(org_uri)
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You do not have permission to perform this action.",
            response.json()["detail"],
        )
        # user no org
        self.client.force_authenticate(self.user_no_org)
        response = self.client.delete(org_uri)
        self.assertEqual(404, response.status_code)
        self.assertCountEqual(response.json()["errors"], {"organization": "Not found."})

    def test_correct_leave_org(self):
        """Members of org without owner role can leave the org"""
        # admin user
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(org_leave_uri)
        self.assertEqual(204, response.status_code)
        # common user
        self.client.force_authenticate(self.user_common_org_1)
        response = self.client.post(org_leave_uri)
        self.assertEqual(204, response.status_code)

    def test_error_leave_org(self):
        """Owner of an org or user without membership of an org cannot leave an org"""
        # owner user
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(org_leave_uri)
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "Owner cannot leave the organization but can choose to delete the organization.",
            response.json()["errors"],
        )
        # no org user
        self.client.force_authenticate(self.user_no_org)
        response = self.client.post(org_leave_uri)
        self.assertEqual(404, response.status_code)
        self.assertCountEqual(response.json()["errors"], {"organization": "Not found."})

    def test_correct_remove_user_from_org(self):
        """Only users with admin or owner roles can remove users from their org"""
        # owner remove a user
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_admin2_org_1.username}
        )
        self.assertEqual(204, response.status_code)
        # admin remove a user
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_common_org_1.username}
        )
        self.assertEqual(204, response.status_code)

    def test_error_remove_user_from_org(self):
        """
        1 - common user cannot remove users (owner, admin or other user)
        2 - admin cannot remove neither the owner nor other admin
        3 - request without a username
        4 - request with a username not existing
        5 - request with a valid username, but it's not a member
        6 - request with a valid username and member of another org
        7 - user with no org
        """
        # 1 - common user cannot remove users (owner, admin or other user)
        self.client.force_authenticate(self.user_common_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_admin_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_common2_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        # 2 - admin cannot remove neither the owner nor other admin
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual("Cannot remove organization owner.", response.json()["detail"])
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_admin2_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual("Cannot remove another admin.", response.json()["detail"])
        # 3 - request without a username
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(org_remove_member_uri, {"username": ""})
        self.assertEqual(400, response.status_code)
        self.assertIn("'username' is required.", response.json()["errors"])
        # 4 - request with a username not existing
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": "not_existing_user"}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("No such member.", response.json()["errors"])
        # 5 - request with a valid username, but it's not a member
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_no_org.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("No such member.", response.json()["errors"])
        # 6 - request with a valid username and member of another org
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_common_org_2.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("No such member.", response.json()["errors"])
        # 7 - user with no org
        self.client.force_authenticate(self.user_no_org)
        response = self.client.post(
            org_remove_member_uri, {"username": self.user_common_org_2.username}
        )
        self.assertEqual(404, response.status_code)

    def test_correct_invite(self):
        """Owner and admins can invite users"""
        # owner can invite
        self.client.force_authenticate(self.user_owner_org_2)
        response = self.client.post(org_invite_uri, {"username": self.user_no_org})
        self.assertEqual(201, response.status_code)
        Invitation.objects.get(user=self.user_no_org, organization=self.org_2).delete()
        self.client.force_authenticate(self.user_owner_org_2)
        response = self.client.post(org_invite_uri, {"username": self.user_no_org})
        self.assertEqual(201, response.status_code)

    def test_error_invite(self):
        """
        1 - Cannot invite member
        2 - Common user cannot invite members
        3 - Cannot invite without username nor blank
        4 - Cannot invite not existing username
        5 - Cannot invite if an invite is already pending
        6 - Cannot invite if max member number is reached
        7 - cannot invite if no member of org
        """
        # 1 - Cannot invite member
        self.client.force_authenticate(self.user_owner_org_2)
        response = self.client.post(
            org_invite_uri, {"username": self.user_common_org_2}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("Invite failed.", response.json()["errors"])
        # 2 - Common user cannot invite members
        self.client.force_authenticate(self.user_common_org_2)
        response = self.client.post(org_invite_uri, {"username": self.user_no_org})
        self.assertEqual(403, response.status_code)
        # 3 - Cannot invite without username
        self.client.force_authenticate(self.user_owner_org_2)
        response = self.client.post(org_invite_uri)
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {"username": ["This field is required."]}, response.json()["errors"]
        )
        response = self.client.post(org_invite_uri, {"username": ""})
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            {"username": ["This field may not be blank."]}, response.json()["errors"]
        )
        # 4 - Cannot invite not existing username
        self.client.force_authenticate(self.user_owner_org_2)
        response = self.client.post(org_invite_uri, {"username": "not_existing_user"})
        self.assertEqual(400, response.status_code)
        self.assertEqual({"detail": "Failed"}, response.json()["errors"])
        # 5 - Cannot invite if an invitation is already pending
        with transaction.atomic():
            self.client.force_authenticate(self.user_owner_org_2)
            response = self.client.post(
                org_invite_uri, {"username": self.user_invited.username}
            )
            self.assertEqual(400, response.status_code)
            self.assertIn("Invite failed.", response.json()["errors"])
        # 6 - Cannot invite if max member number is reached
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(
            org_invite_uri, {"username": self.user_no_org.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            Invitation.MaxMemberException.default_detail, response.json()["errors"]
        )
        # 7 - cannot invite if no member of org
        self.client.force_authenticate(self.user_no_org)
        response = self.client.post(
            org_invite_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(404, response.status_code)

    def test_correct_remove_admin_from_org(self):
        """Only owner can remove user as admin from their org"""
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_admin2_org_1.username}
        )
        self.assertEqual(204, response.status_code)

    def test_error_remove_admin_from_org(self):
        """
        1 - common user cannot remove admins
        2 - an admin cannot remove other admin
        3 - request without a username
        4 - request with a username not existing
        5 - request with a valid username, but it's not a member
        6 - request with a valid username and member of another org
        7 - user with no org
        """
        # 1 - common user cannot remove admin
        self.client.force_authenticate(self.user_common_org_1)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_admin_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        # 2 - an admin cannot remove other admin
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You can't modify owner permission.", response.json()["detail"]
        )
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_admin2_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual("You are not the owner of the org.", response.json()["detail"])
        # 3 - request without a username
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(org_remove_admin_uri, {"username": ""})
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "This field may not be blank.", response.json()["errors"]["username"]
        )
        # 4 - request with a username not existing
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_admin_uri, {"username": "not_existing_user"}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "User to promote/remove is not part of your organization.",
            response.json()["errors"]["detail"],
        )
        # 5 - request with a valid username, but it's not a member
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_no_org.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "User to promote/remove is not part of your organization.",
            response.json()["errors"]["detail"],
        )
        # 6 - request with a valid username and member of another org
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_common_org_2.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "User to promote/remove is not part of your organization.",
            response.json()["errors"]["detail"],
        )
        # 7 - user with no org
        self.client.force_authenticate(self.user_no_org)
        response = self.client.post(
            org_remove_admin_uri, {"username": self.user_common_org_2.username}
        )
        self.assertEqual(404, response.status_code)

    def test_correct_promote_admin_from_org(self):
        """Only owner can promote user as admin from their org"""
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_common_org_1.username}
        )
        self.assertEqual(200, response.status_code)

    def test_error_promote_admin_from_org(self):
        """
        1 - common user cannot promote admins
        2 - an admin cannot promote other admin
        3 - request without a username
        4 - request with a username not existing
        5 - request with a valid username, but it's not a member
        6 - request with a valid username and member of another org
        7 - user with no org
        """
        # 1 - common user cannot promote admin
        self.client.force_authenticate(self.user_common_org_1)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_admin_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        # 2 - an admin cannot promote other admin
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_owner_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(
            "You can't modify owner permission.", response.json()["detail"]
        )
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_admin2_org_1.username}
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual("You are not the owner of the org.", response.json()["detail"])
        # 3 - request without a username
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(org_promote_admin_uri, {"username": ""})
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "This field may not be blank.", response.json()["errors"]["username"]
        )
        # 4 - request with a username not existing
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_promote_admin_uri, {"username": "not_existing_user"}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "User to promote/remove is not part of your organization.",
            response.json()["errors"]["detail"],
        )
        # 5 - request with a valid username, but it's not a member
        self.client.force_authenticate(self.user_admin_org_1)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_no_org.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "User to promote/remove is not part of your organization.",
            response.json()["errors"]["detail"],
        )
        # 6 - request with a valid username and member of another org
        self.client.force_authenticate(self.user_owner_org_1)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_common_org_2.username}
        )
        self.assertEqual(400, response.status_code)
        self.assertIn(
            "User to promote/remove is not part of your organization.",
            response.json()["errors"]["detail"],
        )
        # 7 - user with no org
        self.client.force_authenticate(self.user_no_org)
        response = self.client.post(
            org_promote_admin_uri, {"username": self.user_common_org_2.username}
        )
        self.assertEqual(404, response.status_code)
