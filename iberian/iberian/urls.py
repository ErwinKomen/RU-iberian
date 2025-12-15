"""
Definition of urls for iberian.
"""

from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.conf.urls import include #, url 
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseNotFound
from django.urls import path, re_path
import django.contrib.auth.views
import django

import iberian
from iberian import views

# Import from iberian as a whole
from iberian.settings import APP_PREFIX, STATIC_ROOT

# Other Django stuff
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy, path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
from django.views.static import serve

import iberian.seeker.views
from iberian.seeker.views import *

admin.autodiscover()


# Set admin stie information
admin.site.site_header = "Iberian Saints"
admin.site.site_title = "Iberian Admin"

pfx = APP_PREFIX
use_testapp = False

# ================ Custom error handling when debugging =============
def custom_page_not_found(request, exception=None):
    return iberian.saints.views.view_404(request)

handler404 = custom_page_not_found

urlpatterns = [
    # ============ STANDARD VIEWS =====================
    re_path(r'^$', iberian.saints.views.home, name='myhome'),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': STATIC_ROOT}), 
    path("404/", custom_page_not_found),
    re_path(r'^favicon\.ico$',RedirectView.as_view(url='/static/saints/content/favicon.ico')),
    
    # ============ SAINTS VIEWS =======================
    re_path('', include(('iberian.saints.urls',  'saints'), namespace="saints")),

    # ============ SEEKER views =======================

    re_path(r'^upload/list', UploadListView.as_view(), name='upload_list'),
    re_path(r'^upload/details(?:/(?P<pk>\d+))?/$', UploadDetails.as_view(), name='upload_details'),
    re_path(r'^upload/edit(?:/(?P<pk>\d+))?/$', UploadEdit.as_view(), name='upload_edit'),
    re_path(r'^upload/process(?:/(?P<pk>\d+))?/$', UploadProcess.as_view(), name='upload_process'),

    # ============ MAP views =======================
    re_path(r'^iberian/map/', csrf_exempt(IberianMapView.as_view()), name='iberian_map'),
    re_path(r'^church/map/', csrf_exempt(ChurchMapView.as_view()), name='church_map'), # OK?
    re_path(r'^manuscript/map/', csrf_exempt(ManuscriptMapView.as_view()), name='manuscript_map'), # OK?
    re_path(r'^inscription/map/', csrf_exempt(InscriptionMapView.as_view()), name='inscription_map'), # OK?
    re_path(r'^object/map/', csrf_exempt(ObjectMapView.as_view()), name='object_map'), # OK?
    re_path(r'^littext/map/', csrf_exempt(LiteraryMapView.as_view()), name='littext_map'), # OK?

    # =============================================================================================

    # For working with ModelWidgets from the select2 package https://django-select2.readthedocs.io
    re_path(r'^select2/', include('django_select2.urls')),

    re_path(r'^definitions$', RedirectView.as_view(url='/'+pfx+'admin/'), name='definitions'),
    re_path(r'^nlogin', iberian.seeker.views.nlogin, name='nlogin'),
    re_path(r'^signup/$', iberian.seeker.views.signup, name='signup'),

    re_path(r'^login/user/(?P<user_id>\w[\w\d_]+)$', iberian.seeker.views.login_as_user, name='login_as'),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls, name='admin_base'),
]

#if iberian.settings.DEBUG:
#    urlpatterns += staticfiles_urlpatterns()