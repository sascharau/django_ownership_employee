from typing import Union
from rest_framework import permissions
from .utils import valid_owner
from rest_framework.request import Request
from members.api.views import ActivateUser, PasswordResetConfirmView, RegisterView, ResetPasswordView


class IsAnonymous(permissions.BasePermission):

    def has_permission(self, request: Request,
                       view: Union[RegisterView, ResetPasswordView, ActivateUser, PasswordResetConfirmView]) -> bool:
        user = request.user
        return user.is_anonymous


class FlamingoPermission(permissions.DjangoModelPermissions):

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']:
            return valid_owner(obj, request.user)

    def get_view_perm(self, method, model_cls):
        # todo check ob mann das noch braucht ab Django 2.1
        if method == 'GET':
            for perm, description in model_cls._meta.permissions:
                if perm[:4] == 'view':
                    return [model_cls._meta.app_label + '.' + perm]
                else:
                    return None
        else:
            return None

    def has_permission(self, request, view, ):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
                not request.user.is_authenticated and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        extra = self.get_view_perm(request.method, queryset.model)
        if extra is not None:
            perms.extend(extra)
        return request.user.has_perms(perms)
