# from django.conf.urls import url
from django.urls import path, re_path
from . import views

# TEMPLATE URLS
app_name = 'saints'

urlpatterns = [
    path('', views.home, name='home'), # get and post req. for insert operation
    path('register/', views.register , name='register'), # Sign up
    path('logout/', views.user_logout, name='logout'), # Logout
    path('login/', views.user_login, name='user_login'), # Login

    path('church/new/', views.edit_church, name='church-insert'), # get and post req. for insert operation
    path('church/new/<str:view>/', views.edit_church, name='church-insert'),
    path('church/new/<int:pk>', views.edit_church, name='church-update'), # get and post req. for update operation
    path('church/new/<int:pk>/<str:focus>', views.edit_church, name='church-update'),
    path('church/delete/<int:id>/', views.churchDelete, name='church-delete'),
    path('church/list/', views.churchList, name='church-list'),  # get request to retrieve and display all records
    path('church/<int:pk>', views.ChurchDetailView.as_view(), name='church-detail'),

    path('bibliography/new/', views.bibliographyCreate, name='bibliography-insert'), # get and post req. for insert operation
    path('bibliography/new/<int:id>/', views.bibliographyCreate, name='bibliography-update'), # get and post req. for update operation
    path('bibliography/delete/<int:id>/', views.bibliographyDelete, name='bibliography-delete'),
    path('bibliography/list/', views.bibliographyList, name='bibliography-list'),  # get request to retrieve and display all records

    re_path(r'^inscription/new/$', views.edit_inscription, name='inscription-insert'),
    path('inscription/new/<str:view>/', views.edit_inscription, name='inscription-insert'),
    path('inscription/new/<int:pk>', views.edit_inscription, name='inscription-update'), # get and post req. for update operation
    path('inscription/new/<int:pk>/<str:focus>', views.edit_inscription, name='inscription-update'),
    # re_path(r'^inscription/new/(?P<pk>\d+)/$', views.InscriptionUpdateView.as_view(), name='inscription-update'),
    re_path(r'^inscription/delete/(?P<pk>\d+)/$', views.InscriptionDeleteView.as_view(), name='inscription-delete'),
    path('inscription/list', views.InscriptionList, name='inscription-list'),
    path('inscription/<int:pk>', views.InscriptionDetailView.as_view(), name='inscription-detail'),

    re_path(r'^saint/new/$', views.edit_saint, name='saint-insert'),
    path('saint/new/<str:view>/', views.edit_saint, name='saint-insert'),
    path('saint/new/<int:pk>', views.edit_saint, name='saint-update'),
    path('saint/new/<int:pk>/<str:focus>', views.edit_saint, name='saint-update'),
    re_path(r'^saint/delete/(?P<pk>\d+)/$', views.SaintDeleteView.as_view(), name='saint-delete'),
    path('saint/<int:pk>', views.SaintDetailView.as_view(), name='saint-detail'),
    path('saint/list', views.SaintList, name='saint-list'),

    re_path(r'^object/new/$', views.edit_object, name='object-insert'),
    path('object/new/<int:pk>', views.edit_object, name='object-update'),
    path('object/new/<int:pk>/<str:focus>', views.edit_object, name='object-update'),
    re_path(r'^object/delete/(?P<pk>\d+)/$', views.ObjectDeleteView.as_view(), name='object-delete'),
    path('object/list', views.ObjectList, name='object-list'),
    path('object/<int:pk>', views.ObjectDetailView.as_view(), name='object-detail'),

    re_path(r'^feast/new/$', views.FeastCreatView.as_view(), name='feast-insert'),
    re_path(r'^feast/new/(?P<pk>\d+)/$', views.FeastUpdateView.as_view(), name='feast-update'),
    re_path(r'^feast/delete/(?P<pk>\d+)/$', views.FeastDeleteView.as_view(), name='feast-delete'),
    path('feast/list', views.FeastListView.as_view(), name='feast-list'),

    re_path(r'^liturgicalmanuscript/new/$', views.edit_liturgicalmanuscript, name='liturgicalmanuscript-insert'),
    path('liturgicalmanuscript/new/<str:view>/', views.edit_liturgicalmanuscript, name='liturgicalmanuscript-insert'),
    path('liturgicalmanuscript/new/<int:pk>', views.edit_liturgicalmanuscript, name='liturgicalmanuscript-update'),
    path('liturgicalmanuscript/new/<int:pk>/<str:focus>', views.edit_liturgicalmanuscript, name='liturgicalmanuscript-update'),
    re_path(r'^liturgicalmanuscript/delete/(?P<pk>\d+)/$', views.LiturgicalManuscriptDeleteView.as_view(), name='liturgicalmanuscript-delete'),
    path('liturgicalmanuscript/list', views.LiturgicalManuscriptList, name='liturgicalmanuscript-list'),
    path('liturgicalmanuscript/<int:pk>', views.LiturgicalManuscriptDetailView.as_view(), name='liturgicalmanuscript-detail'),

    re_path(r'^rite/new/$', views.RiteCreatView.as_view(), name='rite-insert'),
    re_path(r'^rite/new/(?P<pk>\d+)/$', views.RiteUpdateView.as_view(), name='rite-update'),
    re_path(r'^rite/delete/(?P<pk>\d+)/$', views.RiteDeleteView.as_view(), name='rite-delete'),
    path('rite/list', views.RiteListView.as_view(), name='rite-list'),

    re_path(r'^manuscripttype/new/$', views.ManuscriptTypeCreatView.as_view(), name='manuscripttype-insert'),
    re_path(r'^manuscripttype/new/(?P<pk>\d+)/$', views.ManuscriptTypeUpdateView.as_view(), name='manuscripttype-update'),
    re_path(r'^manuscripttype/delete/(?P<pk>\d+)/$', views.ManuscriptTypeDeleteView.as_view(), name='manuscripttype-delete'),
    path('manuscripttype/list', views.ManuscriptTypeListView.as_view(), name='manuscripttype-list'),

    re_path(r'^objecttype/new/$', views.ObjectTypeCreatView.as_view(), name='objecttype-insert'),
    re_path(r'^objecttype/new/(?P<pk>\d+)/$', views.ObjectTypeUpdateView.as_view(), name='objecttype-update'),
    re_path(r'^objecttype/delete/(?P<pk>\d+)/$', views.ObjectTypeDeleteView.as_view(), name='objecttype-delete'),
    path('objecttype/list', views.ObjectTypeListView.as_view(), name='objecttype-list'),

    re_path(r'^sainttype/new/$', views.SaintTypeCreatView.as_view(), name='sainttype-insert'),
    re_path(r'^sainttype/new/(?P<pk>\d+)/$', views.SaintTypeUpdateView.as_view(), name='sainttype-update'),
    re_path(r'^sainttype/delete/(?P<pk>\d+)/$', views.SaintTypeDeleteView.as_view(), name='sainttype-delete'),
    path('sainttype/list', views.SaintTypeListView.as_view(), name='sainttype-list'),

    re_path(r'^institutiontype/new/$', views.InstitutionTypeCreatView.as_view(), name='institutiontype-insert'),
    re_path(r'^institutiontype/new/(?P<pk>\d+)/$', views.InstitutionTypeUpdateView.as_view(), name='institutiontype-update'),
    re_path(r'^institutiontype/delete/(?P<pk>\d+)/$', views.InstitutionTypeDeleteView.as_view(), name='institutiontype-delete'),
    path('institutiontype/list', views.InstitutionTypeListView.as_view(), name='institutiontype-list'),

    re_path(r'^city/new/$', views.CityCreatView.as_view(), name='city-insert'),
    re_path(r'^city/new/(?P<pk>\d+)/$', views.CityUpdateView.as_view(), name='city-update'),
    re_path(r'^city/delete/(?P<pk>\d+)/$', views.CityDeleteView.as_view(), name='city-delete'),
    path('city/list', views.CityListView.as_view(), name='city-list'),

    re_path(r'^region/new/$', views.RegionCreatView.as_view(), name='region-insert'),
    re_path(r'^region/new/(?P<pk>\d+)/$', views.RegionUpdateView.as_view(), name='region-update'),
    re_path(r'^region/delete/(?P<pk>\d+)/$', views.RegionDeleteView.as_view(), name='region-delete'),
    path('region/list', views.RegionListView.as_view(), name='region-list'),

    re_path(r'^museum/new/$', views.MuseumCreatView.as_view(), name='museum-insert'),
    re_path(r'^museum/new/(?P<pk>\d+)/$', views.MuseumUpdateView.as_view(), name='museum-update'),
    re_path(r'^museum/delete/(?P<pk>\d+)/$', views.MuseumDeleteView.as_view(), name='museum-delete'),
    path('museum/list', views.MuseumListView.as_view(), name='museum-list'),
]