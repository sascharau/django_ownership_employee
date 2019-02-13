from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from conf.settings import LOGIN_REDIRECT_URL
from .utils import valid_owner


class IsAnonymous(object):
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return super(IsAnonymous, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)

class MessageMixin:
    success_message = _('Success')
    error_message = _('Please correct the errors below.')
    permission_denied_message = _("You do not have permission to perform this action.")

    def get_permission_denied_message(self):
        return messages.error(self.request, self.permission_denied_message)

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(MessageMixin, self).form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, self.error_message)
        return super(MessageMixin, self).form_invalid(form)


class PermissionMixin(AccessMixin, MessageMixin):
    """
    Flamingo permission is for the employees roles.
    On this point we don't know if the owner/ main user use permission function.

    This is are bit different to the default PermissionRequiredMixin.
    If the User has no permission set. He get all permissions from
    settings.PERMISSION_CODENAME. (In this list only set permissions/apps thar are not
    involved in the security of the System.)

    It doesn't matter if the permission is set in view. It will only
    use if the request.user is in any OwnerGroup withs permission. In this
    Case we now the permission function is in using.

    """
    permission = None
    permission_url = None

    def get_permission(self):
        if self.permission is not None:
            # It can be None. We use PermissionMixin for any view.
            # It is required if the user has any permission set.
            if isinstance(self.permission, str):
                perms = (self.permission, )
            else:
                perms = self.permission
            return perms
        else:
            return None

    def has_permission(self):
        perms = self.get_permission()
        if perms is not None:
            return self.request.user.has_perms(perms)
        else:
            # no permission are set, let the user go
            return True

    def no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        if self.permission_url is None:
            # list views in most of the times
            url = self.success_url
        else:
            # permission_url is set
            url = self.permission_url
        return redirect(url)

    def dispatch(self, *args, **kwargs):
        if not self.has_permission():
            self.get_permission_denied_message()
            return self.no_permission()
        return super().dispatch(*args, **kwargs)


class FlamingoCreateMixin(PermissionMixin, MessageMixin, generic.CreateView):
    template_name = 'form.html'  # default

    def get_form_kwargs(self):
        kwargs = super(FlamingoCreateMixin, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FlamingoCreateMixin, self).dispatch(*args, **kwargs)


class FlamingoUpdateMixin(PermissionMixin, MessageMixin, generic.UpdateView):
    template_name = 'form.html'  # default

    def get_object(self):
        # get object from uidb64
        self.object = urlsafe_base64_decode(self.kwargs['uidb64']).decode()
        return self.model._default_manager.get(pk=self.object)

    def get_form_kwargs(self):
        # add user and update object
        kwargs = super().get_form_kwargs()
        kwargs.update({
                'user': self.request.user,
                'object': self.object.pk
        })
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # check if object has same owner
        obj = self.get_object()
        if valid_owner(obj, self.request.user):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404('404')
