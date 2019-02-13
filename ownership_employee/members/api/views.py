from django.contrib.auth import update_session_auth_hash
from django.utils.translation import ugettext as _
from django.contrib.auth import login

from rest_framework import permissions, generics, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.tokens import RefreshToken

from common import api_mixins

from ..models import UserProfile, User
from ..tokens import get_valid_token_user
from ..emails import (
    send_password_reset_api_email,
    send_api_email_not_found,
    send_activate_email)

from .serializers import (
    SignUpSerializer,
    ChangePasswordSerializer,
    ResetPasswordSerializer,
    ResetPasswordDoneSerializer,
    LoginSerializer,
    UserSerializer)


class RegisterView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [
        permissions.AllowAny,
        api_mixins.IsAnonymous
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = User._default_manager.get(username=serializer.data['email'])
        send_activate_email(request, user, api=True)

        return Response(
            {
                'message': _('We have sent an e-mail to you for verification. '
                             'Follow the link provided to finalize the '
                             'process. Please contact us if you do not '
                             'receive it within a few minutes.')

            },
            status=status.HTTP_201_CREATED,
        )

class AccessMixin(generics.GenericAPIView):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def get_access_token(self, user):
        refresh = self.get_token(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

class ActivateUser(AccessMixin):
    permission_classes = [
        api_mixins.IsAnonymous
    ]

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def get(self, request, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs
        user = get_valid_token_user(kwargs['uidb64'], kwargs['token'])
        if user is not None:
            user.is_active = True
            user.save()
            login(request, user, backend='common.backends.PermissionBackend')
            profile = UserProfile.objects.create(
                user=user,
                is_owner_admin=True,
                owner=user,
            )
            profile.save()
            return Response(self.get_access_token(user),
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(AccessMixin):
    """
    Change Password

    If data valid returns new jwt.

    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # set_password
            self.user.set_password(
                serializer.validated_data['new_password']
            )
            self.user.save()

            # make sure the user stays logged in
            update_session_auth_hash(request, self.user)

            return Response(
                self.get_access_token(self.user),
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(generics.GenericAPIView):
    """

    Send email to verification.
    Work only for Anonymous User.

    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [
        api_mixins.IsAnonymous
    ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.filter(
                    email__iexact=serializer.validated_data['email'],
                    is_active=True
                ).first()
            except User.DoesNotExist:
                user = None

            if user is not None:
                send_password_reset_api_email(
                    request,
                    user
                )

            else:
                send_api_email_not_found(
                    request,
                    serializer.validated_data['email']
                )

            return Response(
                {
                    'message': _('We have sent an e-mail to you for '
                                 'verification. Follow the link provided to '
                                 'finalize the process. Please contact us if '
                                 'you do not receive it within a few minutes.')

                },
                status=status.HTTP_200_OK
            )

        else:

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetConfirmView(AccessMixin):
    """
       Reset Password

       Returns the status 200 and new JWT, user is logged in
           / or error message

       """

    serializer_class = ResetPasswordDoneSerializer
    permission_classes = [
        api_mixins.IsAnonymous
    ]

    def post(self, request, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs
        user = get_valid_token_user(kwargs['uidb64'], kwargs['token'])
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() and user is not None:
            # set_password
            user.set_password(
                serializer.validated_data['new_password']
            )
            user.save()
            login(request, user, backend='common.backends.PermissionBackend')
            return Response(
                self.get_access_token(user),
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class TokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = LoginSerializer



class UserViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.none()
    serializer_class = UserSerializer
    permission_classes = [api_mixins.FlamingoPermission]

    def get_queryset(self):
        return UserProfile.owner_objects.all()
