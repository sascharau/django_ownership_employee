from django.contrib import admin
from .models import UserProfile, OwnerGroup

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(OwnerGroup)