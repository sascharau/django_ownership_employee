from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet)
#router.register('profile', views.ProfileViewSet)


members_list = views.UserViewSet.as_view({
    'get': 'list',
})
# #
# # members_detail = views.ProfileViewSet.as_view({
# #     'get': 'retrieve',
# #     'put': 'update',
# #     'patch': 'partial_update',
# #     'delete': 'destroy'
# # })


urlpatterns = [
    #members
    path(r'', include(router.urls)),

    path('user/', members_list, name='members_list'),

    # auth:
    path('login/',
         views.TokenObtainPairView.as_view(), name='api_login'),

    path('signup/',
         views.RegisterView.as_view(), name='api_signup'),

    path('activate/<uidb64>/<token>/',
         views.ActivateUser.as_view(), name='api_signup_activate'),

    path('change-password/',
         views.ChangePasswordView.as_view(), name='api_change_password'),

    path('reset-password/',
         views.ResetPasswordView.as_view(), name='api_reset_password'),

    path('reset-password-done/<uidb64>/<token>/',
         views.PasswordResetConfirmView.as_view(), name='api_reset_password_done'),

]
