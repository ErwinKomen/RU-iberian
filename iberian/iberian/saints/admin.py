from django.contrib import admin
from django.contrib.admin.models import LogEntry, DELETION
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse

# Own application
from iberian.saints.models import *

# Register your models here.
admin.site.register(Church)
admin.site.register(InstitutionType)
admin.site.register(Bibliography)

# @admin.register(Location)
# class LocationAdmin(OSMGeoAdmin):
#     list_display = ('coordinates',)


# How to display user information
admin.site.unregister(User)
# What to display in a list
UserAdmin.list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login']
# Turn it on again
admin.site.register(User, UserAdmin)

