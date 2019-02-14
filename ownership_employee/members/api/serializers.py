from django.contrib.auth.password_validation import validate_password
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from common.models import User

from ..models import UserProfile, GENDER_CHOICES


class ValidateUser(serializers.Serializer):

    def clean_password_confirm(self, data):
        password_confirm = self.get_initial().get('password_confirm', None)

        if password_confirm:
            password = data['password']
            password_confirm = data['password_confirm']

            if password and password_confirm and password != password_confirm:
                raise ValidationError(
                    _("The password fields didn't match.")
                )
        return data

    def validate_username_email(self, data, **kwargs):
        email = self.get_initial().get('email', None)
        if email:
            qs_username = User.objects.filter(username__iexact=email)
            qs_email = User.objects.filter(email__iexact=email)

            if self.instance:
                # update object
                if qs_username.filter().exclude(pk=self.instance.pk).exists():
                    raise ValidationError(
                        _("E-Mail as username already exists!")
                    )

                elif qs_email.filter().exclude(pk=self.instance.pk).exists():
                    raise ValidationError(
                        _("E-Mail already exists!")
                    )

            else:
                # new object
                if qs_username:
                    raise ValidationError(
                        _("E-Mail as username already exists!")
                    )

                elif qs_email:
                    raise ValidationError(
                        _("E-Mail already exists!")
                    )
        return data

    def clean_password(self, data):
        """check't password if secure enough before check if password in data"""
        password = self.get_initial().get('password', None)
        if password:
            validate_password(self.initial_data['password'], self.instance)
        return data

    def validate(self, data):
        self._added_errors = {}

        try:
            self.clean_password(data)
        except ValidationError as error:
            self._added_errors['password'] = [error]

        try:
            self.validate_username_email(data)
        except ValidationError as error:
            self._added_errors['email'] = [error]

        try:
            self.clean_password_confirm(data)
        except ValidationError as error:
            self._added_errors['password_confirm'] = [error]

        if self._added_errors:
            raise serializers.ValidationError(self._added_errors)

        return data


class LoginSerializer(TokenObtainSerializer):

    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        self.user = authenticate(**{
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        })

        if self.user is None or not self.user.is_active:
            raise serializers.ValidationError(
                _('No active account found with the given credentials'),
            )

        elif not self.user.is_staff and not self.user.profile.owner.is_active:
            msg = _('Your Main Account is disabled.')
            raise serializers.ValidationError(msg)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data


class SignUpSerializer(ValidateUser):
    email = serializers.EmailField(
        max_length=254,
        min_length=8,
        required=True,
        label='E-Mail',
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm')

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            is_active=False,
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, data):
        validate_password(data, self.instance)
        return data

    def validate_old_password(self, data):
        request_data = self.context.get("request")

        if not request_data.user.check_password(data):
            raise serializers.ValidationError(
                _('The old password is Invalid')
            )

        else:
            return data


class ResetPasswordSerializer(serializers.Serializer):
    """ in any case we send a email """
    email = serializers.EmailField(
        write_only=True,
        required=True,
    )


class ResetPasswordDoneSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})

    def validate_new_password(self, data):
        validate_password(data, self.instance)
        return data



class UserSerializer(serializers.HyperlinkedModelSerializer, ValidateUser):
    id = serializers.IntegerField(source='pk', read_only=True)
    key = serializers.CharField(source='get_absolute_url', read_only=True)
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    detail_url = serializers.HyperlinkedIdentityField(view_name='userprofile-detail')
    password = serializers.CharField(source='user.password', write_only=True, style={'input_type': 'password'})

    class Meta:
        model = UserProfile
        fields = [
            'key', 'username',
            'email', 'first_name',
            'last_name', 'password', 'gender',
            'detail_url', 'id', 'contact',
            'avatar'
        ]

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if self.instance is not None:
            # remove password if user is update profile
            # we use password only for create members
            self.fields.pop('password')

    def update(self, instance, validated_data):
        # User
        user_data = validated_data.pop('user', None)
        for key, value in user_data.items():
            setattr(instance.user, key, value)

        # UserProfile
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.user.save()
        instance.save()
        return instance

    # def delete():

    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        user = User.objects.create_user(**user_data)
        user.save()

        profile = UserProfile.objects.create(
            user=user,
            owner=self.context['request'].user.profile.owner,
            **validated_data
        )
        profile.save()
        return profile
