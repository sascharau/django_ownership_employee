from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework import status

from common.utils import create_uid
from ..tokens import verified_user_token
from .set_up_members import MembersTestCase

User = get_user_model()


class SignUpTestSerializer(MembersTestCase):

    def setUp(self):
        self.init()

    def test_signup_pass(self):
        counter = User.objects.count()
        url = reverse('api_signup')
        payload = {
            'email': self.USERNAME,
            'password': self.PASSWORD,
            'password_confirm':self.PASSWORD
        }
        response = self.client.post(url, payload,  format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        user = User.objects.get(username=self.USERNAME, email=self.USERNAME)
        self.assertFalse(user.is_active)
        counter_after = User.objects.count()
        self.assertEqual(counter_after, counter + 1)

    def test_signup_activate_api_fail(self):
        uid = 'BH'
        token = 'asfdadsfsdfsdfsdfsdf234324'

        response = self.client.get(
            reverse('api_signup_activate',
                    kwargs={'uidb64': uid, 'token': token}
                    )
        )
        self.assertEqual(response.status_code, 400)

    def test_signup_activate_api(self):
        user = self.test_user
        uid = create_uid(user.pk)
        token = verified_user_token.make_token(user)

        response = self.client.get(
            reverse('api_signup_activate',
                    kwargs={'uidb64': uid, 'token': token}
                    )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            User.objects.get(
                pk=force_text(urlsafe_base64_decode(uid))
            ),
            user
        )
        self.assertTrue(user.profile.is_owner_admin)
        self.assertEqual(user.profile.owner, user)
        self.assertEqual(response.wsgi_request.user, user)
        # check JWT Tocken

    def test_signup_email_fail(self):
        """ Email already exists! """
        url = reverse('api_signup')
        payload = {
            'email': 'test@test.de',
            'password': 'Secret3000',
            'password_confirm': 'Secret3000'
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_signup_password_fail(self):
        counter = User.objects.count()

        url = reverse('api_signup')
        payload = {
            'email': 'foo@foo.de',
            'password': 'Secret3000',
            'password_confirm': 'Secret-55555'
        }

        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(counter, User.objects.count())
        self.assertEqual(len(mail.outbox), 0)
