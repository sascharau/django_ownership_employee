from typing import List, Set
from django.contrib.auth.models import Permission
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from conf import settings
from common.models import User

def get_permissions_list() -> List[str]:
    """
    returns list of permission code names from all
    registered apps in settings.PERMISSION_CODENAME
    """
    permissions = []
    for permission_path in settings.PERMISSION_CODENAME:
        permission = import_string(permission_path)
        for item in permission:
            permissions.append(item)
    if not permissions:
        raise ImproperlyConfigured(
            'No permissions have been defined. Edit PERMISSION_CODENAME = []'
            'in settings and add import strings from your relevant apps to this list.'
        )

    return permissions


permissions_choices = get_permissions_list()


class UserPermissions:

    def get_user_permissions(self, user: User) -> Set[str]:
        # get permissions from OwnerGroup
        user_permission = Permission.objects.filter(ownergroup__userprofile=user.profile)\
            .values_list('content_type__app_label', 'codename')

        if user_permission is None or user.profile.is_owner_admin:
            # if user is not in any ownergroup or he is owner_admin, user
            # get all Permissions from settings.PERMISSION_CODENAME list
            user_permission = Permission.objects.filter(codename__in=get_permissions_list())\
                .values_list('content_type__app_label', 'codename')
        # format query to use request.user.has_perm in views
        permissions_dict = {"%s.%s" % (content_type, codename) for content_type, codename in user_permission}
        return permissions_dict


class PermissionBackend(UserPermissions):
    # this must be register in settings.AUTHENTICATION_BACKENDS

    def authenticate(self, username, password):
        """
        Always return 'None' to prevent authentication within this backend.
        """
        return None

    def has_perm(self, user: User, perm: str, obj: None = None) -> bool:
        if not user.is_active or not user.profile.owner.is_active:
            return False
        # return true if permission is in list
        return perm in self.get_user_permissions(user, obj)
