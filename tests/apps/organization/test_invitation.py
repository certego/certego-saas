import logging

from django.db import transaction
from django.test import tag
from rest_framework.reverse import reverse

from certego_saas.apps.organization.models import Invitation, Membership, Organization

from ... import CustomTestCase, User, setup_custom_user

org_invite_uri = reverse("user_organization-invite")
invitations_uri = reverse("user_invitations-list")


@tag("apps", "organization")
class TestInvitation(CustomTestCase):
    @transaction.atomic
    def setUp(self):
        Membership.objects.all().delete()
        Organization.objects.all().delete()
        Invitation.objects.all().delete()
        # create 2 test users
        self.user1: User = User.objects.get_or_create(username="testinvuser1")[0]
        self.user2: User = User.objects.get_or_create(username="testinvuser2")[0]
        # create client
        self.client = setup_custom_user(self.user1)
        # create test org and test invitation
        self.org: Organization = self.__create_org()
        self.invitation: Invitation = self.__create_invitation(organization=self.org)
        return super().setUp()

    # TEST CASES

    def test_list_200(self):
        # fetch invitations list for user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(invitations_uri)
        content = response.json()
        msg = (response, content)

        # assert for API response
        self.assertEqual(200, response.status_code, msg=msg)
        self.assertGreaterEqual(1, len(content), msg=msg)
        first_inv = content[0]
        self.assertIn("id", first_inv, msg=msg)
        self.assertIn("created_at", first_inv, msg=msg)
        self.assertIn("organization", first_inv, msg=msg)
        self.assertIn("status", first_inv, msg=msg)
        self.assertEqual(Invitation.Status.PENDING, first_inv["status"], msg=msg)
        self.assertEqual(
            self.invitation.organization.name,
            first_inv["organization"]["name"],
            msg=msg,
        )

    def test_delete_204(self):
        """Invitation was created by user1
        who is owner of organization
        so only user1 can delete it too
        """

        # delete invitation
        response = self.__delete_invitation_api(self.invitation.id)

        # assert for API response
        self.assertEqual(204, response.status_code, msg=response)

    def test_delete_403(self):
        """invitation was created by user1
        who is owner of organization,
        so user2 should not be able to delete it
        """

        # delete invitation
        self.client.force_authenticate(user=self.user2)
        with self.assertLogs(level=logging.ERROR):
            response = self.__delete_invitation_api(self.invitation.id)

        # assert for API response
        self.assertEqual(403, response.status_code, msg=response)

    def test_accept_204(self):
        self.assertEqual(
            Invitation.Status.PENDING,
            self.user2.invitations.first().status,
            msg="invitation was created by user1 (org owner) for user2",
        )
        self.assertFalse(
            self.org.user_has_membership(self.user2), msg="user2 has no membership"
        )

        # accept invite
        self.client.force_authenticate(user=self.user2)
        response = self.__accept_invite_api(self.invitation.id)

        # assert for API response
        self.assertEqual(204, response.status_code, msg=response)
        # assert for DB query
        self.user2.refresh_from_db()
        self.assertEqual(
            Invitation.Status.ACCEPTED,
            self.user2.invitations.first().status,
            msg="invitation was accepted",
        )
        self.assertTrue(
            self.org.user_has_membership(self.user2), msg="user2 now has membership"
        )

    def test_accept_400_existing_member(self):
        # user2 is now member of org
        self.test_accept_204()

        # accept invite
        self.client.force_authenticate(user=self.user2)
        response = self.__accept_invite_api(self.invitation.id)
        content = response.json()
        msg = (response, content)
        exc = Membership.ExistingMembershipException
        # assert for API response
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        # assert for DB query
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    def test_accept_400_previously_declined(self):
        # user2 declined invitation
        self.test_decline_204()

        # accept invite
        self.client.force_authenticate(user=self.user2)
        response = self.__accept_invite_api(self.invitation.id)
        content = response.json()
        msg = (response, content)
        exc = Invitation.PreviouslyDeclinedException

        # assert for API response
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        # assert for DB query
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    def test_accept_400_too_many_member(self):
        Organization.MAX_MEMBERS = 1

        # try to accept invite
        self.client.force_authenticate(user=self.user2)
        response = self.__accept_invite_api(self.invitation.id)
        content = response.json()
        msg = (response, content)
        exc = Invitation.MaxMemberException

        # assert for API response
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        # assert for DB query
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

        Organization.MAX_MEMBERS = 3

    def test_decline_204(self):
        self.assertEqual(
            Invitation.Status.PENDING,
            self.user2.invitations.first().status,
            msg="invitation was created by user1 (org owner) for user2",
        )
        self.assertFalse(
            self.org.user_has_membership(self.user2), msg="user2 has no membership"
        )

        # decline invite
        self.client.force_authenticate(user=self.user2)
        response = self.__decline_invite_api(self.invitation.id)

        # assert for API response
        self.assertEqual(204, response.status_code, msg=response)
        # assert for DB query
        self.user2.refresh_from_db()
        self.assertEqual(
            Invitation.Status.DECLINED,
            self.user2.invitations.first().status,
            msg="invitation was declined",
        )
        self.assertFalse(
            self.org.user_has_membership(self.user2), msg="user2 has no membership"
        )

    def test_decline_204_previously_accepted(self):
        # user2 is now member of org
        self.test_accept_204()

        # decline invite
        self.client.force_authenticate(user=self.user2)
        response = self.__decline_invite_api(self.invitation.id)
        content = response.json()
        msg = (response, content)
        exc = Invitation.PreviouslyAcceptedException

        # assert for API response
        self.assertEqual(exc.status_code, response.status_code, msg=msg)
        # assert for DB query
        self.assertIn(exc.default_detail, content["errors"], msg=msg)

    # UTILITY METHODS

    def __delete_invitation_api(self, invitation_id):
        uri = reverse("user_invitations-detail", args=[invitation_id])
        response = self.client.delete(uri)

        return response

    def __accept_invite_api(self, invitation_id):
        uri = reverse("user_invitations-accept", args=[invitation_id])
        response = self.client.post(uri)

        return response

    def __decline_invite_api(self, invitation_id):
        uri = reverse("user_invitations-decline", args=[invitation_id])
        response = self.client.post(uri)

        return response

    def __create_org(self) -> Organization:
        # create org
        self.assertEqual(0, Organization.objects.all().count())
        org = Organization.create(name="testorg", owner=self.user1)
        self.assertEqual(1, Organization.objects.all().count())

        return org

    def __create_invitation(self, organization) -> Invitation:
        # create invitation
        self.assertEqual(0, Invitation.objects.all().count())
        inv = Invitation.objects.create(user=self.user2, organization=organization)
        self.assertEqual(1, Invitation.objects.all().count())

        return inv
