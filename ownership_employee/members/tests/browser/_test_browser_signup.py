from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _

from selenium.webdriver.firefox.webdriver import WebDriver

from conf.settings import LOGIN_REDIRECT_URL
from ...tokens import verified_user_token

UserModel = get_user_model()


class SignUpTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_signup_valid(self):
        user_count = UserModel.objects.count()

        self.selenium.get('%s%s' % (self.live_server_url, reverse('signup')))

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('test@test3000.de')

        password1_input = self.selenium.find_element_by_name("password1")
        password1_input.send_keys('Secret4000')

        password2_input = self.selenium.find_element_by_name("password2")
        password2_input.send_keys('Secret4000')

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

        self.assertEqual(
            UserModel.objects.count(),
            user_count + 1
        )

        self.assertEqual(
            self.selenium.current_url,
            '%s%s' % (self.live_server_url, reverse('account_activation_sent'))
        )

        self.assertEqual(len(mail.outbox), 1)

    def test_signup_error(self):
        self.selenium.get('%s%s' % (self.live_server_url, reverse('signup')))
        self.assertIn("Signup", self.selenium.title)
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('test')

        password1_input = self.selenium.find_element_by_name("password1")
        password1_input.send_keys('Secret4000')

        password2_input = self.selenium.find_element_by_name("password2")
        password2_input.send_keys('Secret4000')

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    # activation view
    def _generate_uid_and_token(self, user):
        key = {}
        key['uid'] = urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        key['token'] = verified_user_token.make_token(user)
        return key

    def test_activation_view(self):
        user = UserModel.objects.create_user(username='test@test3000.de')
        url_kwargs = self._generate_uid_and_token(user)
        url = '/members/activate/'

        self.selenium.get(
            '%s%s%s/%s' % (
                self.live_server_url,
                url,
                url_kwargs['uid'],
                url_kwargs['token']
            )
        )

        self.assertTrue(user.profile.is_owner_admin)
        self.assertEqual(user.profile.owner, user)
        self.assertTrue(user.is_active)

        self.assertEqual(
            self.selenium.current_url,
            '%s%s' % (self.live_server_url, LOGIN_REDIRECT_URL)
        )
