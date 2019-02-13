from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Permission

from common.models import CommonModel, User
from common.backends import permissions_choices


GENDER_CHOICES = (
    (1, _('Male')),
    (2, _('Female')),
)


class UserProfile(CommonModel):
    """
    Profile model
    The owner field allows us to get the main user
    and the employees. CommonModel make the
    workaround easy. Use Model.owner_objects.all() to
    get only the owner specific data.

    """

    user = models.OneToOneField(
        User,
        primary_key=True,
        related_name='profile',
        on_delete=models.CASCADE
    )

    gender = models.PositiveSmallIntegerField(
        _('Gender'),
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        _('Avatar'),
        blank=True,
        null=True,
    )

    is_owner_admin = models.BooleanField(
        default=False
    )

    email_is_verified = models.BooleanField(
        default=False,
        editable=False,
    )

    department = models.ForeignKey(
        'Department',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    owner = models.ForeignKey(
        User,
        editable=True,
        on_delete=models.CASCADE
    )

    forbidden_counter = models.PositiveIntegerField(
        editable=False,
        blank=True,
        default=0
    )

    group = models.ManyToManyField(
        'OwnerGroup',
        blank=True
    )

    class Meta:
        verbose_name = 'User profile'
        verbose_name_plural = 'User profiles'

    def __str__(self):
        return self.user.username


class OwnerGroup(CommonModel):
    """
    The Owner admin can set permissions per Group
    for has employees.

    That is same same bot different as in auth.Group.
    We use CommonModel to get the owner and select
    Permissions from settings.PERMISSION_CODENAME.

    If no permission are set, user get all Permissions
    form the settings.PERMISSION_CODENAME list.
    for safety reasons do not use django auth.permissions etc.
    in this list.
    """
    name = models.CharField(_('Name'), max_length=80)
    permission = models.ManyToManyField(
        Permission,
        limit_choices_to={
            'codename__in': permissions_choices,
        },
        blank=True,
    )

    class Meta:
        verbose_name = _('Owner group')
        verbose_name_plural = _('Owner groups')

    def __str__(self):
        return self.name


class Department(CommonModel):

    name = models.CharField(
        _('_Name'),
        max_length=150
    )

    group = models.ManyToManyField(
        OwnerGroup,
        blank=True
    )

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        permissions = (
            ('change_between_departments',
             _('Can change between Departments')),
        )

    def __str__(self):
        return self.name
