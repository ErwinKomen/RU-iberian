"""
Definition of views for the SEEKER app.
"""

from django.apps import apps
from django.contrib import admin
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group, User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q, Prefetch, Count, F, Sum
from django.db.models.functions import Lower
from django.db.models.query import QuerySet 
from django.forms import formset_factory, modelformset_factory, inlineformset_factory, ValidationError
from django.forms.models import model_to_dict
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.template.loader import render_to_string
from django.template import Context
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.views.generic import ListView, View
from django.views.decorators.csrf import csrf_exempt
import os, json, copy

# ======= imports from my own application ======
from iberian.basic.utils import ErrHandle
from iberian.seeker.models import Upload, get_current_datetime
from iberian.seeker.forms import SignUpForm, UploadForm
from iberian.saints.views import home
from iberian.utilities.views import saintsimplesearch

# ======= from RU-Basic ========================
from iberian.basic.views import BasicPart, BasicList, BasicDetails, make_search_list, add_rel_item, adapt_search
from iberian.settings import MEDIA_ROOT

# RIPD: forms and models
from iberian.saints.forms import SaintForm
from iberian.saints.models import Saint, City, SaintChurchRelation, SaintInscriptionRelation, \
    SaintLitManuscriptRelation

# IBERIAN: mapview app
from iberian.mapview.views import MapView 

# Some constants that can be used
paginateSize = 20
paginateSelect = 15
paginateValues = (100, 50, 20, 10, 5, 2, 1, )


def get_application_name():
    """Try to get the name of this application"""

    # Walk through all the installed apps
    for app in apps.get_app_configs():
        # Check if this is a site-package
        if "site-package" not in app.path:
            # Get the name of this app
            name = app.name
            # Take the first part before the dot
            project_name = name.split(".")[0]
            return project_name
    return "unknown"
# Provide application-specific information
PROJECT_NAME = get_application_name()
app_user = "{}_user".format(PROJECT_NAME.lower())
app_uploader = "{}_uploader".format(PROJECT_NAME.lower())
app_editor = "{}_editor".format(PROJECT_NAME.lower())
app_userplus = "{}_userplus".format(PROJECT_NAME.lower())
app_developer = "{}_developer".format(PROJECT_NAME.lower())
app_moderator = "{}_moderator".format(PROJECT_NAME.lower())

bDebug = False

def user_is_authenticated(request):
    # Is this user authenticated?
    username = request.user.username
    user = User.objects.filter(username=username).first()
    response = False if user == None else user.is_authenticated
    return response

def user_is_ingroup(request, sGroup):
    # Is this user part of the indicated group?
    user = User.objects.filter(username=request.user.username).first()
    response = username_is_ingroup(user, sGroup)
    return response

def username_is_ingroup(user, sGroup):
    # glist = user.groups.values_list('name', flat=True)

    # Only look at group if the user is known
    if user == None:
        glist = []
    else:
        glist = [x.name for x in user.groups.all()]

        # Only needed for debugging
        if bDebug:
            ErrHandle().Status("User [{}] is in groups: {}".format(user, glist))
    # Evaluate the list
    bIsInGroup = (sGroup in glist)
    return bIsInGroup

def user_is_superuser(request):
    bFound = False
    # Is this user part of the indicated group?
    username = request.user.username
    if username != "":
        user = User.objects.filter(username=username).first()
        if user != None:
            bFound = user.is_superuser
    return bFound




# Create your views here.
def nlogin(request):
    """Renders the not-logged-in page."""
    assert isinstance(request, HttpRequest)
    context =  {    'title':'Not logged in', 
                    'message':'Radboud University lila utility.',
                    'year':get_current_datetime().year,}
    context['is_app_uploader'] = user_is_ingroup(request, app_uploader)
    return render(request,'nlogin.html', context)

def login_as_user(request, user_id):
    assert isinstance(request, HttpRequest)

    # Find out who I am
    supername = request.user.username
    # super = User.objects.filter(username__iexact=supername).first()
    super = User.objects.filter(username=supername).first()
    if super == None:
        return nlogin(request)

    # Make sure that I am superuser
    if super.is_staff and super.is_superuser:
        # user = User.objects.filter(username__iexact=user_id).first()
        user = User.objects.filter(username=user_id).first()
        if user != None:

            # Check it the account is active
            if user.is_active:
                # Log the user in.
                login(request, user)
                # Go to the home page
                response = redirect(reverse("myhome"))
                return response
            else:
                # If account is not active:
                return HttpResponse("The account of {} is not active.".format(user.username))

    # Go to the home page
    response = redirect(reverse("myhome"))
    return response

def signup(request):
    """Provide basic sign up and validation of it """

    context = {'registered': False}
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the form
            form.save()
            # Create the user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # also make sure that the user gets into the STAFF,
            #      otherwise he/she may not see the admin pages
            user = authenticate(username=username, 
                                password=raw_password,
                                is_staff=False)
            # Default settings: 
            user.is_staff = False
            user.is_active = False
            # Safe using the defaults
            user.save()
            # Add user to the "iberian_user" group
            gQs = Group.objects.filter(name=app_user)
            if gQs.count() > 0:
                g = gQs[0]
                g.user_set.add(user)

            # Set the 'registered' flag in the context
            context['registered'] = True
            ## Log in as the user
            #login(request, user)
            #return redirect(reverse("myhome"))
    else:
        form = SignUpForm()
    # Make sure the form ends up in the context
    context['form'] = form
    # return render(request, 'signup.html', {'form': form})
    return render(request, 'signup.html', context)


# =================================== OTHER VIEWS ===================================================


class UploadEdit(BasicDetails):
    """The details of one author"""

    model = Upload
    mForm = UploadForm
    prefix = 'upl'
    title = "Upload"
    has_select2 = True
    no_delete = False
    mainitems = []
    lSaintsExcel = [
        {"xfield": "Unnamed: 0",    "type": "skip"}, 
        {"xfield": "name",          "type": "str",     "lfield": "name" }, 
        {"xfield": "SEMM name",     "type": "str",     "lfield": "semm_name"}, 
        {"xfield": "death_date",    "type": "custom",  "lfield": "death_date"}, 
        {"xfield": "feast_day",     "type": "str",     "lfield": "feast_day"}, 
        {"xfield": "City",          "type": "fk_str",  "lfield": "death_city",      "cls": "City"}, 
        {"xfield": "region",        "type": "fk_str",  "lfield": "location_region", "cls": "Region"},                                              
        {"xfield": "Liturgical Type", "type": "fk_str","lfield": "ltype",           "cls": "LiturgicalType"}, 
        {"xfield": "Saint Type",    "type": "fk_str",  "lfield": "type",            "cls": "SaintType"}, 
        {"xfield": "description",   "type": "str",     "lfield": "description"}, 
        {"xfield": "id",            "type": "id",      "lfield": "id"}, 
        {"xfield": "status",        "type": "bool",    "lfield": "status"}, 
        ]

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            #user_id = self.request.user.id if instance.user is None else instance.user.id
            #user = None if user_id is None else User.objects.filter(id=user_id).first()

            # Make sure we know the user id
            user_id = instance.user.id

            # Get the info now, because some processing may take place
            sButtonInfo = self.get_buttons(instance)

            # Define the main items to show and edit
            context['mainitems'] = [
                # -------- HIDDEN field values ---------------
                {'type': 'plain', 'label': "User:",         'value': user_id,          'field_key': 'user', 'empty': 'hide'},
                # --------------------------------------------
                {'type': 'plain', 'label': "User:",         'value': instance.user.username                     },
                {'type': 'plain', 'label': "Name:",         'value': instance.name,             'field_key': "name" },
                {'type': 'safe',  'label': "File:",         'value': instance.get_upload_file(),'field_key': "upfile" },
                {'type': 'plain', 'label': "Info:",         'value': instance.get_info()                        },
                {'type': 'plain', 'label': "Last saved:",   'value': instance.get_saved()                       },
                {'type': 'plain', 'label': "Status:",       'value': instance.get_status()                      },
                {'type': 'safe',  'label': "",              'value': sButtonInfo                                },
                ]

            # Signal that we have select2
            context['has_select2'] = True

            context['upload_id'] = instance.id
            context['after_details'] = render_to_string("seeker/upload_process.html", context, self.request)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("UploadEdit/add_to_context")

        # Return the context we have made
        return context

    def before_save(self, form, instance):
        bResult = True
        sBack = ""
        if not instance is None:
            if instance.user is None:
                instance.user = self.request.user
        return bResult, sBack

    def get_buttons(self, instance):
        """Create button(s) for reading the contents, supposing there is any JSON contents"""

        sBack = ""
        oErr = ErrHandle()
        lHtml = []
        sText = ""

        try:
            # Check if there is a file uploaded
            if not instance.upfile is None and not instance.upfile.name is None:
                # Get the fullinfo as a string
                bResult, sBack = instance.read_fullinfo(self.lSaintsExcel, force=True)

                if bResult and sBack != "":
                    # It has been read: is this valid json?
                    oText = json.loads(sBack)
                    # Getting here means all is well

                    # Getting here means we can create a button to process it
                    lHtml.append('<a class="btn btn-xs jumbo-3" role="button" ')
                    lHtml.append('   onclick="document.getElementById(\'process_upload\').submit();">')
                    lHtml.append('Process the upload</a>')
                    # Combine into string
                    sBack = "\n".join(lHtml)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("UploadEdit/get_buttons")
            sBack = msg
        return sBack


class UploadDetails(UploadEdit):
    """Html variant of UploadEdit"""

    rtype = "html"


class UploadListView(BasicList):
    """Details of uploads"""

    model = Upload
    listform = UploadForm
    prefix = "upl"
    has_select2 = False
    new_button = True
    order_cols = ['user__username', 'name', 'status', 'saved']
    order_default = order_cols
    order_heads = [
        {'name': 'User',    'order': 'o=1', 'type': 'str', 'custom': 'username',    'linkdetails': True},
        {'name': 'Name',    'order': 'o=2', 'type': 'str', 'field':  'name',        'linkdetails': True},
        {'name': 'Status',  'order': 'o=3', 'type': 'str', 'field':  'status',      'linkdetails': True, 'main': True},
        {'name': 'Saved',   'order': 'o=4', 'type': 'str', 'custom': 'saved'}
        ]
    filters = [ {"name": "Name",    "id": "filter_name",    "enabled": False},
                {"name": "User",    "id": "filter_user",    "enabled": False},
               ]
    searches = [
        {'section': '', 'filterlist': [
            {'filter': 'name',  'dbfield': 'name', 'keyS': 'name'},
            {'filter': 'user',  'fkfield': 'user', 'keyFk': 'username', 'keyList': 'userlist', 'infield': 'id' }
            ]}
        ]

    def get_field_value(self, instance, custom):
        sBack = ""
        sTitle = ""
        html = []
        oErr = ErrHandle()
        try:
            if custom == "username":
                html.append(instance.user.username)
            elif custom == "saved":
                html.append(instance.get_saved())

            # Combine the HTML code
            sBack = "\n".join(html)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("UploadListView/get_field_value")

        return sBack, sTitle


class UploadProcess(UploadDetails):
    """Actually process the upload"""

    initRedirect = True

    def custom_init(self, instance):
        data = dict(status="ok")
        oErr = ErrHandle()
        try:
            # Figure out where to go to after processing this
            self.redirectpage = reverse('upload_details', kwargs={'pk': instance.id})

            if not instance is None and user_is_ingroup(self.request, app_editor):
                # Start the processing of the contents
                instance.do_process()

                # Log that this has been done
                print("UploadProcess: done id {}".format(instance.id))

        except:
            msg = oErr.get_error_message()
            oErr.DoError("UploadProcess")

        return None

# =================================== MAP ===================================================

class IberianMapView(MapView):
    model = Saint 
    modEntry = City
    frmSearch = None 
    order_by = []
    use_object = False
    use_own_entries = True
    label = ""
    language = ""
    param_list = ""
    prefix = "ibn"
    filterQ = None
    city_count = 0

    def initialize(self):
        super(IberianMapView, self).initialize()
        
        # Entries with a 'form' value # AANPASSEN kijk, hier is selectie verdwenen
        self.entry_list = []

        # Moet hier niet ook niet lst_church, _inscrip, _etc worden gebruikt? Of allemaal andere mapviews voor Church, Inscription etc?
        
        # Repeat the query for ourselves         
        lst_saint = saintsimplesearch(self.request, 'saints', 'saint').values(
            "death_city__id", 
            "saintchurchrelation__church__city__id",
            "saintinscriptionrelation__inscription__original_location_city__id", 
            "saintlitmanuscriptrelation__liturgical_manuscript__original_location_city__id"
            )
        # this results in a queryset of saints - but not of cities
        # maar niet resultaat van query zelf
        print(lst_saint)
        lst_city = []
        
        for oSaint in lst_saint:
            city_death = oSaint.get("death_city__id")
            city_church = oSaint.get("saintchurchrelation__church__city__id")
            city_inscr = oSaint.get("saintinscriptionrelation__inscription__original_location_city__id")
            city_lman = oSaint.get("saintlitmanuscriptrelation__liturgical_manuscript__original_location_city__id")
            # Add to list
            if not city_death is None and not city_death in lst_city:
                lst_city.append(city_death)
            if not city_church is None and not city_church in lst_city:
                lst_city.append(city_church)
            if not city_inscr is None and not city_inscr in lst_city:
                lst_city.append(city_inscr)
            if not city_lman is None and not city_lman in lst_city:
                lst_city.append(city_lman)
        city_count = len(lst_city)        
        qs_city = City.objects.filter(id__in=lst_city) 
        city_count = len(qs_city)
        self.qs = qs_city     

    def make_entry_list(self):
        """Create a list of entries for the map"""

        def add_one_entry(id, city, keyword, saint_name, info):
            """Add one entry int [lst_entry]"""
            
            # First combine the the x and y coordinates
            point_lat = str(city.latitude)
            #print(point_lat)            
            point_lon = str(city.longitude)
            #print(point_lon)        
            point = point_lat + ", " + point_lon
            #print(point)

            oErr = ErrHandle()
            try:
                oEntry = dict(saint_id=id, locname=city.name, point = point, point_x=point_lat, point_y=point_lon,
                              keyword=keyword, saint_name=saint_name, info=info)
                lst_back.append(oEntry)
            except:
                msg = oErr.get_error_message()
                oErr.DoError("SaintMapview/add_one_entry")
            return lst_back

        lst_back = []
        oErr = ErrHandle()
        try:
            qs_city = self.qs
            for city in qs_city: #Automatisch? Voor Kerken moet dat niet.
                # (1) Check for which saints this is death_city
                for saint in city.cities.all():
                    # Add this entry
                    if saint.death_date:
                        death_year = saint.death_date.date.year
                    else:
                        death_year = None
                    add_one_entry(saint.id, city, "city", saint.name, death_year)
                # (2) Check for which saints this city has a church
                for rel in SaintChurchRelation.objects.filter(church__city=city):
                    # Add this entry
                    add_one_entry(rel.saint.id, city, "church", rel.saint.name, rel.church.name)
                # (3) Check for which saints this city has an inscription
                for rel in SaintInscriptionRelation.objects.filter(inscription__original_location_city=city):
                    # Add this entry
                    add_one_entry(rel.saint.id, city, "inscription", rel.saint.name, rel.inscription.reference_no)
                # (4) Check which manuscripts are associated with this city via the saint
                for rel in SaintLitManuscriptRelation.objects.filter(liturgical_manuscript__original_location_city=city):
                    # Add this entry
                    add_one_entry(rel.saint.id, city, "manuscript", rel.saint.name, rel.liturgical_manuscript.shelf_no)
            
        except:
            msg = oErr.get_error_message()
            oErr.DoError("IberianMapView/make_entry_list")
        return lst_back
        
    def get_popup(self, dialect):
        """Create a popup from the 'key' values defined in [initialize()]"""

        # Wordt dit gebruikt?

        pop_up = '<p class="h6">{}</p>'.format(dialect['origstr'])
        pop_up += '<hr style="border: 1px solid green" />'
        pop_up += '<p style="font-size: medium;"><span style="color: purple;">{}</span> </p>'.format(dialect['findspot'])
        return pop_up

    def get_group_popup(self, oPoint):
        """Create a popup from the 'key' values defined in [initialize()]"""

        # Figure out what the link would be to this list of items

        # Gaat dit wel helemaal goed?
        params = ""
        oErr = ErrHandle()
        try:
            if self.param_list != None:
                params = "&{}".format( "&".join(self.param_list))
            url = "{}?{}-location={}{}".format(reverse('saints:saint-list'), self.prefix, oPoint['locid'], params) # what is the correct reverse?

            # Create the popup
            pop_up = '<p class="h4">{}</p>'.format(oPoint['findspot'])
            pop_up += '<hr style="border: 1px solid green" />'

            popup_title_1 = "Show" 
            popup_title_2 = "objects in the list" 
                                
            pop_up += '<p style="font-size: large;"><a href="{}" title="{} {} {}"><span style="color: purple;">{}</span> in: {}</a></p>'.format(
                url, popup_title_1, oPoint['count'], popup_title_2, oPoint['count'], oPoint['findspot']) 
        except:
            msg = oErr.get_error_message()
            oErr.DoError("get_group_popup")
        #print(pop_up)
        return pop_up

    def group_entries(self, lst_this):
        """Allow changing the list of entries"""

        oErr = ErrHandle()
        exclude_fields = ['point', 'point_x', 'point_y', 'pop_up', 'locatie', 'country', 'city']
        try:
            # We need to create a new list, based on the 'point' parameter 
            set_point = {}
            for oEntry in lst_this: # ok in lst_this zit alles wel ok volgens mij
                #print(oEntry)
                point = oEntry['point']
                #if not point in set_point:
                # Create a new entry 
                set_point[point] = dict(count=0, items=[], point=point,                                                                                      
                                        trefwoord=oEntry['keyword'],                                            
                                        locid=oEntry['info'],                                            
                                        findspot=oEntry['locname'] 
                                        )
                # Retrieve the item from the set
                oPoint = set_point[point]
                # Add this entry
                oPoint['count'] += 1
                oItem = {}
                for k,v in oEntry.items():
                    print(k, v) # hier zitten de kw's er in
                    if not k in exclude_fields:
                        oItem[k] = v
                oPoint['items'].append(oItem) # Ok wat gebeurt hier precies?

            # Review them again
            lst_back = []
            for point, oEntry in set_point.items():
                # Create the popup
                # print name?
                oEntry['pop_up'] = self.get_group_popup(oEntry) 
                # Add it to the list we return
                lst_back.append(oEntry)
                #print(lst_back)

            total_count = len(lst_back)

            # 131 voor:
            # Return the new list TH hierna mis
            lst_this = copy.copy(lst_back)
            print(lst_this)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("group_entries")

        return lst_this # dit klopt, maar




# ============= THE END ==============================================================================