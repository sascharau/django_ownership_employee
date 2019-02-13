from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.encoding import force_bytes
from django.contrib.auth.models import Permission
from common.models import User
from rest_framework.test import APIClient, APITestCase
from members.models import UserProfile, OwnerGroup


class MembersTestCase(APITestCase):

    USERNAME = 'bar@bar.de'
    PASSWORD = 'Secret4000'
    NEW_PASS = 'NewSecret5000'

    def init(self):
        self.csrf_client = APIClient(enforce_csrf_checks=True)

        self.test_user = User.objects.create_user(
            username='test@test.de',
            password='secret3000',
        )

        self.owner_one = User.objects.create_user(
            username='owner_one@test.de',
            password=self.PASSWORD,
            first_name='Peter',
            email='owner_one@test.de'
        )

        UserProfile.objects.create(
            user=self.owner_one,
            owner=self.owner_one,
            is_owner_admin=True,
        )

        self.owner_one_member = User.objects.create_user(
            username='owner_one_member@test.de',
            password=self.NEW_PASS,
            first_name='CoolBoy',
            email='owner_one_member@test.de'
        )

        UserProfile.objects.create(
            user=self.owner_one_member,
            owner=self.owner_one,
            is_owner_admin=False,
        )

        self.file = SimpleUploadedFile(
            'filename.png',
            content=force_bytes('ABC'),
            content_type='image/png'
        )

    def permission_init(self):
        self.permission = Permission.objects.all()

        self.owner_one_group = OwnerGroup.objects.create(
            name='owner_one_group',
            user=self.owner_one
        )

        self.owner_one_group.permission.set([
            self.permission.get(codename='view_userprofile'),
            self.permission.get(codename='add_userprofile')
        ])

        self.owner_one_member.profile.group.set([
            self.owner_one_group
        ])

        self.owner_one.profile.group.add(
            self.owner_one_group
        )

        self.owner_two = User.objects.create_user(
            username=self.USERNAME,
            password=self.PASSWORD,
            email=self.USERNAME,
            first_name='Peter'
        )

        UserProfile.objects.create(
            user=self.owner_two,
            owner=self.owner_two,
            is_owner_admin=True,
        )
