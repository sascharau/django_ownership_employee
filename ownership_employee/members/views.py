import json

from django.contrib.auth import login, decorators
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, resolve_url
from django.utils.translation import ugettext_lazy as _
from django.views import generic
from django.views.decorators import cache, debug
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http.response import HttpResponseRedirect

from conf import settings
from common import mixins

from .models import UserProfile, User
from .forms import UserChangeForm, UserCreateForm
from .tokens import get_valid_token_user
from .emails import send_activate_email, email_new_user_to_admin
from members.forms import SignUpForm


class SignupView(generic.CreateView, mixins.IsAnonymous):
    form_class = SignUpForm
    success_url = reverse_lazy('account_activation_sent')
    template_name = 'members/form-log-out.html'
    extra_context = {'title': _('Signup')}

    def form_valid(self, form: SignUpForm) -> HttpResponseRedirect:
        self.object = form.save()
        send_activate_email(self.request, self.object)
        return super().form_valid(form)


def account_activation_sent(request):
    ctx = {
        'title': _('Verify Your E-mail Address'),
        'content': _('We have sent an E-mail to you for verification. '
                     'Follow the link provided to finalize the '
                     'process. Please contact us if you do not receive it '
                     'within a few minutes.'
                     )
    }
    return render(request, 'members/form-done-log-out.html', ctx)


@debug.sensitive_post_parameters()
@cache.never_cache
def activate(request: WSGIRequest, uidb64: str, token: str) -> HttpResponseRedirect:
    # check token and try to get user
    user = get_valid_token_user(uidb64, token)
    if user is not None:
        user.is_active = True
        user.save()
        login(request, user,
              backend='django.contrib.auth.backends.ModelBackend')

        UserProfile.objects.create(
            user=user,
            is_owner_admin=True,
            email_is_verified=True,
            owner=user,
        )

        messages.success(request, _('welcome'))
        admin_email_content = 'new user: %s' % user
        email_new_user_to_admin(request.user, admin_email_content )
        return redirect(settings.LOGIN_REDIRECT_URL)

    else:
        ctx = {
            'extra_context': 'Error'
        }
        return render(request, 'members/form-done-log-out.html', ctx)


class EditOwnProfile(mixins.FlamingoUpdateMixin):
    form_class = UserChangeForm
    success_url = reverse_lazy('profile')
    extra_context = {'title': _('Edit your profile')}
    success_message = _('Your profile was successfully updated!')

    def get_object(self) -> User:
        return User.objects.get(id=self.request.user.id)


class CreateMemberView(mixins.FlamingoCreateMixin):
    form_class = UserCreateForm
    success_url = reverse_lazy('members_list')
    extra_context = {'title': _('Create Member')}
    success_message = _('Member was successfully create!')
    permission = 'members.add_userprofile'


class UpdateMemberView(mixins.FlamingoUpdateMixin):
    model = User
    form_class = UserChangeForm
    success_url = reverse_lazy('members_list')
    extra_context = {'title': _('Edit Employees')}
    success_message = _('Member was successfully updated!')
    permission = 'members.change_userprofile'


@decorators.login_required
def members_list(request):
    """
    returns page and call data with ajax after page is load
    views.members_list_ajax

    """
    ctx = {

        'title': _('Members List'),
        'create_url': reverse('create_member'),
        'columns': [_('Edit'), _('Name'), _('Username'), _('State')],
        'api_url': reverse('members_list_ajax')
    }
    return render(request, 'list.html', ctx)


@decorators.login_required
def members_list_ajax(request):
    if request.is_ajax():
        # use owner_objects to get only the owner data
        object_list = UserProfile.owner_objects.all()
        all_item_list = []

        for item in object_list:
            edit_url = resolve_url('update_member', uidb64=(item.get_uidb64()))
            if item.user.is_active:
                active = '<span class="label label-primary"> active </span>'
            else:
                active = '<span class="label label-danger"> inactive </span>'

            list = [
                '<a href="' + edit_url + '">' +
                    '<i class="fa fa-pencil-square-o"></i>' +
                '</a>',
                '<a href="' + edit_url + '">'
                    + item.user.get_full_name() +
                '</a>',
                item.user.username,
                active
            ]
            all_item_list.append(list)
        return HttpResponse(json.dumps({'data': all_item_list}))

#
# def invitations(request):
#     if request.method == 'POST':
#         user_list = request.
# check liste , ; ' '
# for x in y:
# atomic -> user_crate; profile_crate ;send password vergessen email
