from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.utils.functional import SimpleLazyObject

from .models import UserProfile, GENDER_CHOICES, User


def create_clean_email(email: str) -> str:
    """ use this only for create change """

    if User.objects.filter(username__iexact=email).exists():
        raise forms.ValidationError(
            _("Email already exists as Username!")
        )

    if User.objects.filter(email__iexact=email).exists():
        raise forms.ValidationError(
            _("E-Email already exists!")
        )
    return email


class SignUpForm(UserCreationForm):
    """
    In registration process, the new user must enter email address.
    We use this as username. After registration the user can
    change username in profile. if you touch any user functions,
    check if email address is unique!

    """

    username = forms.EmailField(
        max_length=254,
        label='E-Mail',
    )

    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(),
        strip=False
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(),
        strip=False
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )

    def clean_username(self) -> str:
        username = self.cleaned_data['username']
        if User.objects.filter(email__iexact=username).exists():
            raise forms.ValidationError(
                _("E-Email already exists!")
            )
        return username

    def clean_email(self):
        create_clean_email(self.cleaned_data['username'])

    def save(self, commit: bool = True) -> User:
        user = super(SignUpForm, self).save(commit=False)
        user.email = self.cleaned_data['username']
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user


class AuthenticationExtendedForm(AuthenticationForm):
    """ Login check if user and owner is active  """
    def confirm_login_allowed(self, user: User):
        # todo check if email_is_verified and make view

        if not user.profile.email_is_verified:
            messages.warning(self.request, _('Place verified you E-Mail address'))

        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

        if not user.is_staff and not user.profile.owner.is_active:
            raise forms.ValidationError(
                _("Your main user account is inactive. Place contact the main User/Admin."),
                code='inactive',
            )


class BaseUserForm(forms.ModelForm):
    # add profile fields to base class
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    avatar = forms.FileField(required=False)
    email = forms.EmailField(required=False, label='E-Mail')

    class Meta:
        model = User
        fields = [
            'email',
            'first_name', 'last_name',
            'gender', 'avatar'
        ]


class UserCreateForm(BaseUserForm):
    """ Create Member """

    def clean_email(self) -> str:
        return create_clean_email(self.cleaned_data['email'])

    def __init__(self, *args, **kwargs) -> None:
        self.creator = kwargs.pop('user', None)
        super(UserCreateForm, self).__init__(*args, **kwargs)
        # add password field to UserCreateForm
        self.fields['password'] = forms.CharField(
            label=_("Password"),
            widget=forms.PasswordInput(),
            strip=False
        )

    def save(self, commit: bool = True) -> SimpleLazyObject:
        self.user = super(UserCreateForm, self).save(commit=False)
        self.user.set_password(self.cleaned_data["password"])
        self.user.username = self.cleaned_data['email']
        if commit:
            self.user.save()

            profile = UserProfile.objects.create(
                user=self.user,
                owner=self.creator.profile.owner,
                gender=self.cleaned_data["gender"],
            )
            if self.cleaned_data["avatar"]:
                profile.save()
        return self.creator


class UserChangeForm(BaseUserForm):
    """ Update Member """

    def clean_email(self) -> None:
        email = self.cleaned_data['email']
        if self.cleaned_data['email']:
            # check if email exists exclude member
            if User.objects.filter(email__iexact=email)\
                    .exclude(id=self.object_pk).exists():

                raise forms.ValidationError(
                    _("E-Email already exists!")
                )
            # check if email exists as username exclude member
            elif User.objects.filter(username__iexact=email)\
                    .exclude(id=self.object_pk).exists():

                raise forms.ValidationError(
                    _("Email already exists as Username!")
                )

            else:
                return email

    def __init__(self, *args, **kwargs) -> None:
        self.creator = kwargs.pop('user', None)
        self.object_pk = kwargs.pop('object', None)
        self.member = super(UserChangeForm, self).__init__(*args, **kwargs)
        # add profile instance to form
        self.fields['gender'].initial = self.instance.profile.gender
        self.fields['avatar'].initial = self.instance.profile.avatar

    def save(self, *args, **kwargs) -> User:
        user = super(UserChangeForm, self).save(*args, **kwargs)
        user.save()

        user.profile.gender = self.cleaned_data["gender"]
        user.profile.save()
        return user
