from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model
from django.core import mail

from selenium.webdriver.firefox.webdriver import WebDriver

from conf import settings

User = get_user_model()

class AuthTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.test_user = User(
            username='test@test.de',
            password='secret3000',
        )
        self.test_user.save()

    def test_login_valid(self):
        suffix = settings.LOGIN_REDIRECT_URL
        prefix = str(settings.LOGIN_URL + '?next=')

        self.selenium.get('%s%s' % (self.live_server_url, suffix))

        self.assertEqual(
            # redirection to login
            self.selenium.current_url,
            '%s%s' % (self.live_server_url, str(prefix + suffix))
        )

        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('test@test.de')

        password1_input = self.selenium.find_element_by_name("password")
        password1_input.send_keys('secret3000')

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    def change_password(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    '/members/password-change/'))
        passwordold_input = self.selenium.find_element_by_name("old_password")
        passwordold_input.send_keys('secret3000')

        password1_input = self.selenium.find_element_by_name("new_password1")
        password1_input.send_keys('secret5000')

        password2_input = self.selenium.find_element_by_name("new_password2")
        password2_input.send_keys('secret5000')

        self.selenium.find_element_by_xpath('//button[@type="submit"]').click()

    def logout(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/members/logout/'))
        self.assertEqual(
            self.selenium.current_url,
            '%s%s' % (self.live_server_url, settings.LOGIN_URL))

    def reset_password(self):
        self.selenium.get('%s%s' % (self.live_server_url,
                                    '/members/password-reset/'))

        self.assertEqual(self.selenium.current_url,
                         '%s%s' % (self.live_server_url,
                                   '/members/password-reset/done/'))

        self.assertEqual(len(mail.outbox), 1)
