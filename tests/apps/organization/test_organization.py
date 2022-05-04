import logging

from django.db import transaction
from django.test import tag
from rest_framework.reverse import reverse

from certego_saas.apps.organization.models import Invitation, Membership, Organization

from ... import CustomTestCase, User, setup_custom_user

org_uri = reverse("user_organization-list")
org_leave_uri = reverse("user_organization-leave")
org_invite_uri = reverse("user_organization-invite")
org_remove_member_uri = reverse("user_organization-remove-member")


@tag("apps", "organization")
class TestOrganization(CustomTestCase):
    @classmethod
    def setUpClass(cls):
        # create 2 test users
        cls.user1: User = User.objects.get_or_create(username="testorguser1")[0]
        cls.user2: User = User.objects.get_or_create(username="testorguser2")[0]
        # setup client
        cls.client = setup_custom_user(cls.user1)
        return super(TestOrganization, cls).setUpClass()

    @transaction.atomic
    def setUp(self):
        Membership.objects.all().delete()
        Organization.objects.all().delete()
        self.user1.refresh_from_db()
        self.user2.refresh_from_db()
        self.client.force_authenticate(user=self.user1)
        return super().setUp()

    # TEST CASES

    def test_get_org_expand_200(self):
        self.assertEqual(0, Organization.objects.count(), msg="No organization exists")

        # create org
        org = self.__create_org_add_member()

        # API get call
        response = self.client.get(f"{org_uri}?expand=members,pending_invitations")
        content = response.json()
        msg = (response, content)

        # asserts
        self.assertEqual(1, Organization.objects.count(), msg="1 organization exists")

        self.assertEqual(200, response.status_code, msg=msg)
        self.assertEqual(org.name, content["name"], msg=msg)
        self.assertEqual(2, content["members_count"], msg=msg)
        self.assertTrue(content["is_user_owner"], msg=msg)
        self.assertEqual(self.user1.username, content["owner"]["username"], msg=msg)
        self.assertEqual(2, len(content["members"]), msg=msg)
        self.assertIn("pending_invitations", content, msg=msg)

    def test_create_201_400(self):
        # creating new org should return 201
        response = self.client.post(org_uri, data={"name": "testOrg1"})
        content = response.json()
        msg = (response, content)

        self.assertEqual(201, response.status_code, msg=msg)
        self.assertEqual("testOrg1", content["name"], msg=msg)
        self.assertEqual(self.user1.username, content["owner"]["username"], msg=msg)
        self.assertEqual(1, content["members_count"], msg=msg)
        self.assertTrue(content["is_user_owner"], msg=msg)

        # creating new org when org exists should return 400
        response = self.client.post(org_uri, data={"name": "testOrg2"})
        content = response.json()
        msg = (response, content)

        self.assertEqual(400, response.status_code, msg=msg)
        self.assertIn(
            Membership.ExistingMembershipException.default_detail,
            content["errors"],
            msg=msg,
        )

    def test_delete_204(self):
        """
        Org's owner is user1, so can delete the org
        """
        self.__create_org_add_member()

        # /remove_member API call
        response = self.client.delete(org_uri)

        # assert API response
        self.assertEqual(204, response.status_code, msg=response)

    def test_delete_403(self):
        """
        Org's owner is user1, user2 is just a member so can't delete the org
        """
        self.__create_org_add_member()

        # /remove_member API call
        self.client.force_authenticate(user=self.user2)
        with self.assertLogs(level=logging.ERROR):
            response = self.client.delete(org_uri)

        # assert API response
        self.assertEqual(403, response.status_code, msg=response)

    def test_leave_204(self):
        """
        Org's owner is user1, user2 is just a member so can leave
        """
        self.__create_org_add_member()

        # /remove_member API call
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(org_leave_uri)

        # assert API response
        self.assertEqual(204, response.status_code, msg=response)

    def test_leave_400_owner_cant_leave(self):
        """
        Org's owner is user1, so can't leave
        """
        self.__create_org_add_member()

        # /remove_member API call
        response = self.client.post(org_leave_uri)
        content = response.json()
        msg = (response, content)
        exc = Membership.OwnerCantLeaveException

        # assert API response
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    def test_invite_201(self):
        # create org
        org = Organization.create(name="testorg", owner=self.user1)
        self.user1.refresh_from_db()

        self.assertEqual(
            0, self.user2.invitations.count(), msg="currently user2 has no invitations"
        )

        # invite user2
        response, content = self.__send_invite(self.user2.get_username())
        msg = (response, content)

        # asserts
        self.assertEqual(201, response.status_code, msg=msg)

        # user2 should have one invitation
        self.assertEqual(1, self.user2.invitations.count(), msg=msg)
        self.assertEqual(org, self.user2.invitations.first().organization, msg=msg)

    def test_invite_400_invalid_username(self):
        # create org
        _ = Organization.create(name="testorg", owner=self.user1)
        self.user1.refresh_from_db()

        # invite an invalid username
        response, content = self.__send_invite("blahblahblah")
        msg = (response, content)

        # asserts
        self.assertEqual(400, response.status_code, msg=msg)
        self.assertIn("Failed", content["errors"]["detail"], msg=msg)

    def test_invite_400_cant_invite_owner(self):
        # create org
        _ = Organization.create(name="testorg", owner=self.user1)
        self.user1.refresh_from_db()

        # invite self user
        response, content = self.__send_invite(self.user1.get_username())
        msg = (response, content)
        exc = Invitation.OwnerException

        # asserts
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    def test_invite_400_existing_member(self):
        # create org and add member
        self.__create_org_add_member()

        # invite user2
        response, content = self.__send_invite(self.user2.get_username())
        msg = (response, content)
        exc = Invitation.AlreadyPresentException

        # asserts
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    def test_invite_400_already_pending(self):
        # create org
        _ = Organization.create(name="testorg", owner=self.user1)
        self.user1.refresh_from_db()

        # invite user 2
        response, content = self.__send_invite(self.user2.get_username())
        self.assertEqual(201, response.status_code, msg=(response, content))
        # invite user2 again
        response, content = self.__send_invite(self.user2.get_username())
        msg = (response, content)
        exc = Invitation.AlreadyPendingException

        # asserts
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    def test_invite_400_too_many_members(self):
        # forcing 1 member max
        Organization.MAX_MEMBERS = 1
        # create org
        _ = Organization.create(name="testorg", owner=self.user1)
        self.user1.refresh_from_db()
        # invite user 2
        response, content = self.__send_invite(self.user2.get_username())
        exc = Invitation.MaxMemberException
        msg = (response, content)
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        self.assertIn(exc.default_detail, content["errors"], msg=msg)
        Organization.MAX_MEMBERS = 3

    def test_remove_member_204(self):
        self.__create_org_add_member()

        # /remove_member API call
        response = self.__remove_member(self.user2.get_username())

        # assert API response
        self.assertEqual(204, response.status_code, msg=response)

    def test_remove_member_400_no_username(self):
        self.__create_org_add_member()

        # /remove_member API call
        response = self.client.post(org_remove_member_uri)
        content = response.json()
        msg = (response, content)

        # assert API response
        self.assertEqual(400, response.status_code, msg=msg)

    def test_remove_member_400_cant_remove_owner(self):
        self.__create_org_add_member()

        # /remove_member API call
        response = self.__remove_member(self.user1.get_username())
        content = response.json()
        msg = (response, content)

        # assert API response
        self.assertEqual(400, response.status_code, msg=msg)

    def test_remove_member_400_no_such_member(self):
        self.__create_org_add_member()

        # /remove_member API call
        response = self.__remove_member("blahblahblah")
        content = response.json()
        msg = (response, content)

        # assert API response
        self.assertEqual(400, response.status_code, msg=msg)
        self.assertIn("No such member.", content["errors"], msg=msg)

    # UTILITY METHODS

    def __create_org_add_member(self):
        # create org
        org = Organization.create(name="testorg", owner=self.user1)

        # add user2 as member
        self.assertFalse(self.user2.has_membership(), msg="user2 has no membership")
        Membership.objects.create(user=self.user2, organization=org)
        self.assertTrue(self.user2.has_membership(), msg="user2 now has membership")

        return org

    def __send_invite(self, username):
        resp = self.client.post(org_invite_uri, {"username": username})
        return resp, resp.json()

    def __remove_member(self, username):
        return self.client.post(org_remove_member_uri, {"username": username})
