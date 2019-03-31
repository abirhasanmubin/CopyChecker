from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CUser, Profile
# Register your models here.

admin.site.register(CUser)
admin.site.register(Profile)
