from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from common.utils import create_uid
from members.tests.set_up_members import MembersTestCase

class CreateGroups(MembersTestCase):

    def setUp(self):
        self.init()
        self.permission_init()

    def test_view_permission(self):
        c = self.client
        logged_in = c.login(username=self.owner_one_member.username, password=self.NEW_PASS)
        self.assertTrue(logged_in)
        c.user = self.owner_one_member
        response = c.get(reverse('create_member'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.owner_one_member.profile.group.all().first(), 'owner_one_group')
        self.assertTrue(self.owner_one_member.has_perm('members.view_userprofile'))
        self.assertTrue(self.owner_one_member.has_perm('members.add_userprofile'))
        self.assertFalse(self.owner_one_member.has_perm('members.change_userprofile'))
        self.assertFalse(self.owner_one_member.has_perm('members.delete_userprofile'))

    def test_owner_fail(self):
        user_from_different_owner = self.owner_two
        c = self.client
        c.login(username=self.owner_one_member.username, password=self.NEW_PASS)
        c.user = self.owner_one_member
        response = c.get(reverse('update_member', kwargs={'uidb64': create_uid(user_from_different_owner.pk)}))
        self.assertEqual(response.status_code, 404)
