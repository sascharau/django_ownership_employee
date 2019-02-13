from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from rest_framework import status

from common.utils import create_uid
from ..tokens import verified_user_token
from .set_up_members import MembersTestCase

User = get_user_model()


class TestMembersAPICase(MembersTestCase):

    def setUp(self):
        self.init()

    def test_reset_password(self):
        """ reset password valid """
        url = reverse('api_reset_password')
        payload = {
            'email': 'test@test.de',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_reset_password_done(self):
        """ reset password valid """
        user = self.owner_one
        uid = create_uid(user.pk)
        token = verified_user_token.make_token(user)

        response = self.csrf_client.post(
            reverse('api_reset_password_done',
                    kwargs={'uidb64': uid, 'token': token}),
            data={'new_password': 'NEWpassword3000'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.wsgi_request.user, user)
        assert user.is_authenticated is True
        assert response.data['refresh'] is not None
        assert response.data['access'] is not None

    def test_reset_password_done_fail(self):
        """ password fail """
        user = User.objects.get(username='test@test.de')
        uid = create_uid(user.pk)
        token = verified_user_token.make_token(user)

        response = self.csrf_client.post(
            reverse('api_reset_password_done',
                    kwargs={'uidb64': uid, 'token': token}),
            data={'new_password': '3000'}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_email_not_exist(self):
        """
        Email not exist but we send "not found" message
        """
        url = reverse('api_reset_password')
        payload = {
            'email': 'email@not-exist.io',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)

    def test_change_password(self):
        self.client.login(username=self.owner_one.username, password=self.PASSWORD)
        assert self.owner_one.is_authenticated is True

        url = reverse('api_change_password')
        payload = {
            'old_password': self.PASSWORD,
            'new_password': 'BestSecret3000'
        }

        response = self.client.post(url, data=payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert self.owner_one.is_authenticated is True
        assert response.data['refresh'] is not None
        assert response.data['access'] is not None

    def test_login(self):
        url = reverse('api_login')
        login_payload = {
            "username": self.owner_one.username,
            "password": self.PASSWORD
        }
        response = self.client.post(url, data=login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert self.owner_one.is_authenticated is True
        assert response.data['refresh'] is not None
        assert response.data['access'] is not None

