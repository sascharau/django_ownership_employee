from django.db import models
from django.contrib.auth.models import User
from common.dirtyfields.dirtyfields import DirtyFieldsMixin
from common.utils import get_current_user, create_uid


def SET_OWNER(collector, field, sub_objs, using):
    if field.user == get_current_user():
        return models.CASCADE(collector, field, sub_objs, using)
    else:
        collector.add_field_update(field, field.get_owner(), sub_objs)


class CommonManager(models.Manager):

    def get_queryset(self, request=None):
        user = get_current_user()
        if user and user.is_authenticated:
            return super().get_queryset().filter(
                user__profile__owner=user.profile.owner,
            )
        else:
            return None


class CommonModel(DirtyFieldsMixin, models.Model):

    ENABLE_M2M_CHECK = True

    created_at = models.DateField(
        auto_now_add=True,
        editable=False,
        null=True
    )

    modified_at = models.DateField(
        auto_now=True,
        editable=False,
        null=True
    )

    user = models.ForeignKey(
        User,
        editable=False,
        related_name='%(class)s_created',
        on_delete=SET_OWNER
    )

    modified_by = models.ForeignKey(
        User,
        null=True,
        editable=False,
        related_name='%(class)s_modified',
        on_delete=models.SET_NULL
    )

    active = models.BooleanField(
        default=True
    )

    objects = models.Manager()
    owner_objects = CommonManager()

    def get_uidb64(self):
        return create_uid(self.pk)

    def get_owner(self):
        return self.user.profile.owner

    def is_shard_object(self, cls):

        """ if it make since we cant share
        objects withs differnet owners

        if the user is edit this object
        he have to get_or_create neu object.

        if we create new object we have to update all
        ForeignKeys to the new owner object as wall. """

        count = cls.default_manager.filter(pk=self)\
            .values('user__profile__owner').distinct().count()
        if count > 1:
            return True
        else:
            return False

    def save(self, *args, **kwargs) -> None:
        current_user = get_current_user()
        if current_user and current_user.is_authenticated:
            if self.pk:
                self.modified_by = current_user
            else:
                self.user = current_user

        super(CommonModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True
