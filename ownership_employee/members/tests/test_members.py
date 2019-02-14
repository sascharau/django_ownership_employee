from django.urls import reverse
from django.core import mail

from common.models import User
from common.utils import create_uid, get_uid_object
from members.models import UserProfile
from members.forms import SignUpForm, UserChangeForm, UserCreateForm
from members.tokens import verified_user_token
from members.tests.set_up_members import MembersTestCase


class SignUpTestForm(MembersTestCase):

    def setUp(self):
        self.init()

    def test_signup_pass(self):
        form = SignUpForm(data={
            'username': self.USERNAME,
            'password1': self.PASSWORD,
            'password2': self.PASSWORD
            }
        )
        self.assertTrue(form.is_valid())

    def test_signup_email_fail(self):
        """ Email and Email as username already exists! """
        form = SignUpForm(data={
            'username': self.test_user,
            'password1': self.PASSWORD,
            'password2': self.PASSWORD
            }
        )
        self.assertFalse(form.is_valid())
        # check error massige

    def test_signup_email_fail_2(self):
        """ Email already exists! """
        form = SignUpForm(data={
                'username': self.owner_one.email,
                'password1': self.PASSWORD,
                'password2': self.PASSWORD
            }
        )
        self.assertFalse(form.is_valid())
        # check error massige

    def test_signup_password_fail(self):
        """ password fail """
        form = SignUpForm(data={
            'username': self.USERNAME,
            'password1': self.PASSWORD,
            'password2': self.NEW_PASS,
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_change_user(self):
        """ edit UserProfile """
        form = UserChangeForm(data={
            'gender': 2,
            'avatar': self.file
        }, instance=self.owner_one)
        self.assertTrue(form.is_valid())

    def test_form_create_member(self):
        form = UserCreateForm(data={
            'gender': 1,
            'avatar': self.file,
            'email': 'new_member_for_owner_one@email.com',
            'password': self.PASSWORD,
            'first_name': 'Hans'
        }, instance=self.owner_one)
        self.assertTrue(form.is_valid())


class SignUpTestView(MembersTestCase):

    def setUp(self):
        self.init()

    """ password fail """
    def test_signup_view(self):
        user_count = User.objects.count()

        response = self.client.post(
            reverse('signup'),
            data={
                'username': self.USERNAME,
                'password1': self.PASSWORD,
                'password2': self.NEW_PASS
            }
        )

        self.assertEqual(response.status_code, 200)
        self.failUnless(response.context['form'])
        self.failUnless(response.context['form'].errors)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(User.objects.count(), user_count)

    def test_signup_send_mail(self):
        user_count = User.objects.count()
        response = self.client.post(
            reverse('signup'),
            data={
                'username': self.USERNAME,
                'password1': self.PASSWORD,
                'password2': self.PASSWORD
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), user_count + 1)
        self.assertEqual(
            response['Location'],
            reverse('account_activation_sent')
        )
        self.assertEqual(len(mail.outbox), 1)
        user = User.objects.get(username=self.USERNAME)
        self.assertFalse(user.is_active)
        self.assertEqual(user.username, user.email)

    def test_activate_view(self):
        uid = create_uid(self.test_user.pk)
        token = verified_user_token.make_token(self.test_user)
        response = self.client.get(
            reverse('activate', kwargs={'uidb64': uid, 'token': token})
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_uid_object('auth', 'user', uid), self.test_user)
        self.assertTrue(self.test_user.profile.is_owner_admin)
        self.assertEqual(self.test_user.profile.owner, self.test_user)
        self.assertTrue(self.test_user.is_active)
        self.assertTrue(self.test_user.profile.owner.is_active)
        # email to admin
        self.assertEqual(len(mail.outbox), 1)


class MembersTestView(MembersTestCase):

    def setUp(self):
        self.init()

    def test_profile_view(self):
        """ edit UserProfile """
        c = self.client
        logged_in = c.login(username=self.owner_one.username, password=self.PASSWORD)
        self.assertTrue(logged_in)
        self.assertEqual(self.owner_one.first_name, 'Peter')
        self.assertTrue(self.owner_one.profile.is_owner_admin)

        c.user = self.owner_one
        response = c.post(
            path=reverse('profile'),
            data={
                'gender': 1,
                'avatar': self.file,
                'first_name': 'Hans',
            }
        )
        self.assertEqual(response.status_code, 302)
        self.owner_one.refresh_from_db()
        self.assertEqual(self.owner_one.first_name, 'Hans')
        self.assertEqual(self.owner_one.profile.gender, 1)

    def test_create_member_view(self):
        c = self.client
        c.login(username=self.owner_one.username, password=self.PASSWORD)
        c.user = self.owner_one
        c.post(
            reverse('create_member'),
            data={
                'gender': 2,
                'avatar': self.file,
                'first_name': 'Hans',
                'password': self.PASSWORD,
                'email': 'new_user_for_owner_one@test.io',
            }
        )
        new_user = User.objects.get(
            username='new_user_for_owner_one@test.io',
            first_name='Hans',
            profile__gender=2,
            profile__owner=self.owner_one,
        )
        self.assertTrue(new_user.email, 'new_user_for_owner_one@test.io')

    def test_update_member_view(self):
        c = self.client
        c.login(username=self.owner_one.username, password=self.PASSWORD)
        c.user = self.owner_one
        response = c.post(
            reverse('update_member', kwargs={'uidb64': create_uid(self.owner_one_member.pk)}),
            data={
                'gender': 1,
                'avatar': self.file,
                'first_name': 'Hans',
                'password': self.PASSWORD,
                'username': 'hans@test.de',
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_delete_user(self):
        delete_member = User.objects.get(pk=self.owner_one_member.pk)
        delete_member.delete()
        self.assertFalse(User.objects.filter(username=delete_member.username).exists())
        self.assertFalse(UserProfile.objects.filter(user__username=delete_member.username).exists())
