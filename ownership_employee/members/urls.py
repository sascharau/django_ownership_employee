from django.urls import path
from django.contrib.auth import views as auth_views
from django.utils.translation import ugettext_lazy as _

from conf import settings
from . import views
from .forms import AuthenticationExtendedForm


urlpatterns = [

    path('signup/',
         views.SignupView.as_view(), name='signup'),

    path('account_activation_sent/',
         views.account_activation_sent, name='account_activation_sent'),

    path(r'activate/<uidb64>/<token>/',
         views.activate, name='activate'),

    # auth views
    path('login/',
         auth_views.LoginView.as_view(
             template_name='members/form-log-out.html',
             authentication_form=AuthenticationExtendedForm,
             redirect_authenticated_user=True,
             extra_context={
                 'title': 'Login'
             }
          ),
         name='login'),

    path('logout/',
         auth_views.LogoutView.as_view(
             next_page=settings.LOGIN_URL
         ), name='logout'),

    # auth password-change
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='form.html',
             success_url='/members/password-change/done/',
         ),
         name='password_change'),

    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='form-done.html',
             extra_context={
                'content': _('Your password was successfully updated!')
             }
         ),
         name='password_change_done'),

    # auth password-reset
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
            template_name='members/form-log-out.html',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='members/form-done-log-out.html',
             extra_context={
                'content': _("We've emailed you instructions for setting "
                             "your password, if an account exists "
                             "with the email you entered. "),

                'extra_content': _("If you don't receive an email, "
                                   "please make sure you've entered "
                                   "the address you registered with, "
                                   "and check your spam folder.")
            }
         ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='members/form-log-out.html',
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='members/form-done-log-out.html',
             extra_context={
                 'content': _('Your password has been set. '
                              'You may go ahead and log in now.'),

                 'extra_content': '<a href="' +
                                  settings.LOGIN_URL +
                                  '">Login</a>',
             }

         ),
         name='password_reset_complete'),

    # profile
    path('me/',
         views.EditOwnProfile.as_view(), name='profile'),

    # members
    path('',
         views.members_list, name='members_list'),

    path('create/',
         views.CreateMemberView.as_view(), name='create_member'),

    path('update/<uidb64>/',
         views.UpdateMemberView.as_view(), name='update_member'),

    #path('delete/<uidb64>/',
    #     views.delete_member, name='delete_member'),

    path('ajax-members-list',
         views.members_list_ajax, name='members_list_ajax')
]
