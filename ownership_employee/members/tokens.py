from typing import Optional
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode

from .models import User


class TokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user: User, timestamp: int) -> str:
        login_timestamp = '' if user.last_login is None else user.last_login.replace(microsecond=0, tzinfo=None)
        return '{0}{1}{2}{3}{4}'.format(
            user.pk,
            login_timestamp,
            timestamp,
            user.username,
            user.is_active,
        )

verified_user_token = TokenGenerator()


def get_valid_token_user(uidb64: str, token: str) -> Optional[User]:
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and verified_user_token.check_token(user, token):
        return user

    else:
        return None
