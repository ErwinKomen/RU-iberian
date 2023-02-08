"""
Definition of urls for iberian.
"""

from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.conf.urls import include #, url 
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseNotFound
from django.urls import path, re_path
import django.contrib.auth.views
import django

import iberian
from iberian import views

# Import from iberian as a whole
from iberian.settings import APP_PREFIX

# Other Django stuff
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy, path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView

import iberian.seeker.views


admin.autodiscover()


# Set admin stie information
admin.site.site_header = "Iberian Saints"
admin.site.site_title = "Iberian Admin"

pfx = APP_PREFIX
use_testapp = False

# ================ Custom error handling when debugging =============
def custom_page_not_found(request):
    return iberian.saints.views.view_404(request)

urlpatterns = [
    # ============ STANDARD VIEWS =====================
    re_path(r'^$', iberian.saints.views.home, name='home'),
    path("404/", custom_page_not_found),
    re_path(r'^favicon\.ico$',RedirectView.as_view(url='/static/saints/content/favicon.ico')),
    
    # ============ SAINTS VIEWS =======================
    re_path('', include(('iberian.saints.urls',  'saints'), namespace="saints")),

    # =============================================================================================

    # For working with ModelWidgets from the select2 package https://django-select2.readthedocs.io
    re_path(r'^select2/', include('django_select2.urls')),

    re_path(r'^definitions$', RedirectView.as_view(url='/'+pfx+'admin/'), name='definitions'),
    re_path(r'^nlogin', iberian.seeker.views.nlogin, name='nlogin'),
    re_path(r'^signup/$', iberian.seeker.views.signup, name='signup'),

    re_path(r'^login/user/(?P<user_id>\w[\w\d_]+)$', iberian.seeker.views.login_as_user, name='login_as'),

    re_path(r'^login/$', LoginView.as_view
        (
            template_name= 'login.html',
            authentication_form= iberian.seeker.forms.BootstrapAuthenticationForm,
            extra_context= {'title': 'Log in','year': datetime.now().year,}
        ),
        name='login'),
    re_path(r'^logout$',  LogoutView.as_view(next_page=reverse_lazy('home')), name='logout'),

    # Uncomment the next line to enable the admin:
    re_path(r'^admin/', admin.site.urls, name='admin_base'),
]

