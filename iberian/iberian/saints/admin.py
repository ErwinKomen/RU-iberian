from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Church)
admin.site.register(InstitutionType)
admin.site.register(Bibliography)

# @admin.register(Location)
# class LocationAdmin(OSMGeoAdmin):
#     list_display = ('coordinates',)
