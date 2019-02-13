import os, uuid, random
from threading import local
from typing import Optional, Union

from django.apps import apps
from django.core.handlers.wsgi import WSGIRequest
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.functional import SimpleLazyObject
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.text import slugify

from rest_framework.request import Request

from .models import User

_thread_locals = local()


def set_current_user(user: SimpleLazyObject) -> None:
    _thread_locals.user = user


def get_current_user() -> Optional[SimpleLazyObject]:
    return getattr(_thread_locals, 'user', None)


def file_path(instance: SimpleLazyObject, filename: str) -> str:
    name, ext = os.path.splitext(filename)
    date_str = '%s_%s_%s' % (timezone.now().year, timezone.now().month, instance.user.id)
    return 'private/{0}/{1}/{2}/{3}/{4}{5}/'.format(
        instance.user.profile.owner.pk,
        instance.__class__.__name__.lower(),
        date_str,
        uuid.uuid4(),
        slugify(name),
        ext
    )


def valid_owner(object: SimpleLazyObject, user: User) -> bool:
    """
    check if object from same owner
    if not sum to user.forbidden_counter
    runs True or False

    """
    if object._meta.label_lower == 'auth.user':
        object_owner = object.profile.owner
    else:
        object_owner = object.user.profile.owner

    if object_owner == user.profile.owner:
        return True

    else:
        count = user.profile.forbidden_counter + 1
        user.profile.forbidden_counter = count
        user.profile.save()

        if count > 50:
            user.is_active = False
            user.save()
        return False


def get_uid_object(app_label: str, model_name: str, uidb64: str) -> SimpleLazyObject:
    """ get object by uidb64  """
    uid = urlsafe_base64_decode(uidb64).decode()
    obj = apps.get_model(app_label=app_label, model_name=model_name)._default_manager.get(pk=uid)
    return obj


def create_uid(id: int) -> str:
    """ decode id to uidb64 """
    uid = urlsafe_base64_encode(force_bytes(id)).decode()
    return uid


def get_client_ip(request: Union[WSGIRequest, Request]):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


CODE_LENGTH = 8
CODE_CHARS = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ' + '23456789'
# do not use 1, i, l, 0, O, o and I
SEGMENTED_CODES = False
SEGMENT_LENGTH = 4
SEGMENT_SEPARATOR = "-"
PREFIX = str(timezone.now().year) + SEGMENT_SEPARATOR + str(timezone.now().month) + SEGMENT_SEPARATOR


def generate_key(prefix: str = PREFIX,
                 codelength: int = CODE_LENGTH,
                 segmented: str = SEGMENT_SEPARATOR,
                 segmentlength: int = SEGMENT_LENGTH) -> str:
    key = "".join(random.choice(CODE_CHARS) for i in range(codelength))
    key = segmented.join([key[i:i + segmentlength] for i in range(0, len(key), segmentlength)])
    if not prefix:
        return key
    else:
        return prefix + key


