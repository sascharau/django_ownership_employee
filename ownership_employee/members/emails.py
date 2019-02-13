from typing import Dict, Union
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail, mail_admins
from django.core.handlers.wsgi import WSGIRequest

from rest_framework.request import Request

from conf import settings
from members.tokens import verified_user_token
from members.models import User


protocol = 'https://' if settings.USE_HTTPS else 'http://'


def get_email_message_base(request: Union[WSGIRequest, Request], user: User) -> Dict[str, Union[User, str]]:
    # base email content
    content = {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': verified_user_token.make_token(user),
        'protocol': protocol
    }
    return content


def send_activate_email(request: Union[WSGIRequest, Request], user: User, api: bool = False) -> None:
    subject = 'Activate Your Account'
    email_body = get_email_message_base(request, user)
    kwargs = {'uidb64': email_body['uid'], 'token': email_body['token']}
    if api:
        url = reverse('api_signup_activate', kwargs=kwargs)
    else:
        url = reverse('activate', kwargs=kwargs)

    text = _('Please click on the link below to confirm your registration:'),
    email_body['content'] = text
    email_body['url'] = url
    message = render_to_string('members/email.html', email_body)
    user.email_user(subject, message)


def send_password_reset_api_email(request, user):
    """ this is only for API """
    subject = _('Reset Password')
    email_body = get_email_message_base(request, user)
    # add to base email content
    email_body['content'] = _('Please click on the link below to reset password:'),
    email_body['url'] = reverse('api_reset_password_done',
                                kwargs={'uidb64': email_body['uid'], 'token': email_body['token']})
    message = render_to_string('members/email.html', email_body)
    user.email_user(subject, message)


def send_api_email_not_found(request: Request, email: str) -> None:
    subject = _('Reset Password')
    content = _('We received an account recovery request on %s for %s. '
                'If you meant to sign up for %s ,you can do by '
                'clicking this %s%s%s link.') % (
                  get_current_site(request), email,
                  get_current_site(request), protocol,
                  get_current_site(request), reverse('signup')
              )
    send_mail(subject, content, settings.EMAIL_HOST_USER, [email])


def email_new_user_to_admin(user: User, content: str) -> None:
    # send email to first admin in settings.ADMINS
    mail_admins(user, content)
