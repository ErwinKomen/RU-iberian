from django.shortcuts import render, redirect, get_object_or_404

from iberian.basic.utils import ErrHandle
from .forms import *
from django.utils.decorators import method_decorator

from django.views.generic import (View, TemplateView, ListView,
                                  DetailView, CreateView, UpdateView,
                                  DeleteView)
from django.urls import reverse_lazy

# Extra Imports for the Login and Logout Capabilities
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm


# ========================= OWN APPLICATION IMPORT ========================
from iberian.utilities.views import edit_model
from iberian.utilities.views import saintsimplesearch, churchsimplesearch, objectsimplesearch, inscriptionsimplesearch, \
    liturgicalmanuscriptsimplesearch, ltextsimplesearch

from iberian.basic.views import get_application_context

# =================== Helper functions ===================================

def partial_year_to_date(form, instance, date_field, year_field):
    """Used in [before_save()] to change the date_field"""

    # Get the value of the year_field
    value_year = form.cleaned_data.get(year_field)
    if value_year != "":
        value_year = value_year.zfill(4)
    # This only works if there is an instance
    if instance is None:
        value_date = None
    else:
        # Get the date_field
        value_date = getattr(instance, date_field)
    # If they are the same: don't change
    if value_date != value_year:
        # Check for changes
        if value_date is None or value_date == "" or str(value_date.date.year).zfill(4) != value_year:
            # Adapt the form's instance value
            setattr(form.instance, date_field, value_year)



# =================== Create your views here =============================

def register(request):
    registered = False

    if request.method == 'POST':
        # Get info from "both" forms
        # It appears as one form to the user on the .html page
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)
        # Check to see both forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save User Form to Database
            user = user_form.save()
            # Hash the password
            user.set_password(user.password)
            user.is_active = False
            # Update with Hashed password
            user.save()
            # Now we deal with the extra info!
            # Can't commit yet because we still need to manipulate
            profile = profile_form.save(commit=False)
            # Set One to One relationship between
            # UserForm and UserProfileInfoForm
            profile.user = user
            # Check if they provided a profile picture
            if 'profile_pic' in request.FILES:
                print('found it')
                # If yes, then grab it from the POST form reply
                profile.profile_pic = request.FILES['profile_pic']
            # Now save model
            profile.save()
            # Registration Successful!
            registered = True
        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors, profile_form.errors)
    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()
        profile_form = UserProfileInfoForm()
    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    return render(request, 'saints/registration.html',
                  {'user_form': user_form,
                   'profile_form': profile_form,
                   'registered': registered})


def user_login(request):
    if request.method == 'POST':
        # First get the username and password supplied
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Django's built-in authentication function:
        user = authenticate(username=username, password=password)
        # If we have a user
        if user:
            # Check it the account is active
            if user.is_active:
                # Log the user in.
                login(request, user)
                # Go to the home page
                response = redirect(reverse("myhome"))
                return response
            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {}".format(username))
            return HttpResponse("Invalid login details supplied.")

    else:
        # Nothing has been provided for username or password.
        return render(request, 'saints/login.html', {})


@login_required(login_url='/login/')
def user_logout(request):
    # Log out the user.
    logout(request)
    # Return to homepage.
    return redirect('myhome')


login_required(login_url='/login/')
def password_change(request):
    """Allow the user to change password and then return home"""

    oErr = ErrHandle()
    context = {}
    template_name = "saints/change_password.html"
    registered = False
    try:
        # Must be signed in
        if request.user.is_authenticated:
            # Get the user object
            user = request.user
            # Check if we are just showing the form or responding to it
            if request.method == "POST":
                msg = ""
                # Processing change of password
                # form = UserPasswordChangeForm(data=request.POST)
                form = PasswordChangeForm(user, data=request.POST)
                # Get the form values
                if form.is_valid():
                    # Get the values
                    cleaned_data = form.cleaned_data
                    password_old = cleaned_data.get("old_password")
                    password_new = cleaned_data.get("new_password1")
                    password_new2 = cleaned_data.get("new_password2")
                    if user.check_password(password_old):
                        # Check whether new and new2 are equal
                        if password_new == password_new2 and password_new != "":
                            # Yes, valid: process
                            user.set_password(password_new)
                            user.save()
                            # Change of password was Successful!
                            registered = True
                            
                        else:
                            msg = "Your new password is not the same as your repeated password"
                    else:
                        # There is an error
                        msg = "Your old password is incorrect"
                else:
                    # Form is not valid
                    msg = "The password form is not valid"
                context['registered'] = registered
                context['msg'] =msg
                if registered:
                    # Go to the home page
                    login(request, user)
                    response = redirect(reverse("myhome"))
                else:
                    context['form_auth'] = PasswordChangeForm(user)
                    response = render(request, template_name, context)
            else:
                # This is a get: show the correct form
                context['form_auth'] = PasswordChangeForm(user)
                context['registered'] = registered
                response = render(request, template_name, context)
        else:
            response = user_login(request)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("")

    # Return to homepage.
    return response


#
def home(request, errortype=None):
    """Renders the home page."""

    assert isinstance(request, HttpRequest)
    # Specify the template
    template_name = 'saints/home.html'
    context = {
        'title': 'Iberian saints',
        'user': request.user}

    context = get_application_context(request, context)

    # See if this is the result of a particular error
    if errortype != None:
        if errortype == "404":
            context['is_404'] = True
    x = render(request, "saints/base.html", context)
    # Render and return the page
    return render(request, template_name, context)


def view_404(request, *args, **kwargs):
    return home(request, "404")

@login_required(login_url='/login/')
def edit_church(request, pk=None, focus='', view='complete'):
    """Allow adding a new or editing an existing [Saint] instance"""

    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "date_lower", "year_lower")
        partial_year_to_date(form, instance, "date_upper", "year_upper")

    names = 'churchsaint_formset,churchobject_formset,churchinscription_formset,churchliturgicalmanuscript_formset,churchlink_formset'
    return edit_model(request, __name__, 'Church', 'saints', pk, formset_names=names,
                      focus=focus, view=view, before_save=before_save)


@login_required(login_url='/login/')
def ChurchList(request):
    query_set = churchsimplesearch(request, 'saints', 'church')
    query = request.GET.get("q", "") 

    # Gewoon de cities pakken die aan de churches zijn gekoppeld.
    lst_church = churchsimplesearch(request, 'saints', 'church').values("city__id")

    
    lst_city = [] # Hier komen id's mee
    # Wat gebeurt hier precies? Wat wordt doorgegeven?
    for oChurch in lst_church:
        city_church = oChurch.get("city__id")
       
        # Add to list        
        if not city_church is None and not city_church in lst_city:
            lst_city.append(city_church)        
    city_count = len(lst_city) # Waar gaat dit naartoe?              

    context = {'church_list': query_set,
               'nentries': len(query_set),
               'lentries': city_count,
               'query': query}
    return render(request, 'saints/church_list.html', context)


@login_required(login_url='/login/')
def churchDelete(request, id):
    city = get_object_or_404(Church, pk=id)
    city.delete()
    return redirect('saints:church-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ChurchDetailView(DetailView):
    model = Church


@login_required(login_url='/login/')
def bibliographyCreate(request, id=0):
    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "year", "char_year")

    if request.method == "GET":
        if id == 0:
            form = BibliographyForm()
        else:
            bibliography = Bibliography.objects.get(pk=id)
            form = BibliographyForm(instance=bibliography)
        return render(request, 'saints/bibliography_form.html', {'form': form})
    else:  # request.method == "POST":
        if id == 0:
            form = BibliographyForm(request.POST)
        else:
            bibliography = Bibliography.objects.get(pk=id)
            form = BibliographyForm(request.POST, instance=bibliography)
        if form.is_valid():
            before_save(form, bibliography)
            form.save()
        return redirect('saints:bibliography-list')  # after save redirect to the city list


@login_required(login_url='/login/')
def bibliographyList(request):
    context = {'bibliography_list': Bibliography.objects.all()}
    return render(request, 'saints/bibliography_list.html', context)


@login_required(login_url='/login/')
def bibliographyDelete(request, id):
    city = get_object_or_404(Church, pk=id)
    city.delete()
    return redirect('saints:bibliography-list')


@login_required(login_url='/login/')
def institutionTypeCreate(request, id=0):
    if request.method == "GET":
        if id == 0:
            form = InstitutionTypeForm()
        else:
            institutionType = InstitutionType.objects.get(pk=id)
            form = InstitutionTypeForm(instance=institutionType)
        return render(request, 'saints/institutionType_form.html', {'form': form})
    else:  # request.method == "POST":
        if id == 0:
            form = InstitutionTypeForm(request.POST)
        else:
            institutionType = InstitutionType.objects.get(pk=id)
            form = InstitutionTypeForm(request.POST, instance=institutionType)
        if form.is_valid():
            form.save()
        return redirect('saints:institutionType-list')  # after save redirect to the city list


@login_required(login_url='/login/')
def institutionTypeList(request):
    context = {'institutionType_list': InstitutionType.objects.all()}
    return render(request, 'saints/institutionType_list.html', context)


@login_required(login_url='/login/')
def institutionTypeDelete(request, id):
    city = get_object_or_404(Church, pk=id)
    city.delete()
    return redirect('saints:institutionType-list')


# Class Based Views
# -----------------------------------------------------------------------------------------------------------------------
# @method_decorator(login_required(login_url='/login/'), name='dispatch')
# class InscriptionListView(ListView):
#     model = Inscription
#     template_name = 'installations/inscription_list.html'
#     context_object_name = 'inscriptions'


@login_required(login_url='/login/')
def InscriptionList(request):
    query_set = inscriptionsimplesearch(request, 'saints', 'inscription')
    query = request.GET.get("q", "")

    # Gewoon de cities pakken die aan de churches zijn gekoppeld.
    lst_inscrip = inscriptionsimplesearch(request, 'saints', 'inscription').values("original_location_city_id")
    print(len(lst_inscrip))    
    lst_city = [] # Hier komen id's mee
    # Wat gebeurt hier precies? Wat wordt doorgegeven?
    for oInscrip in lst_inscrip:
        #print(lst_city)
        print(len(lst_city))
        city_inscrip = oInscrip.get("original_location_city_id")
       
        # Add to list        
        if not city_inscrip is None and not city_inscrip in lst_city:
            lst_city.append(city_inscrip) # nog dubbele erin        
    city_count = len(lst_inscrip) # Waar gaat dit naartoe?

        # Nog teveel city

    context = {'inscription_list': query_set,
               'nentries': len(query_set),
               'lentries': city_count,
               'query': query}
    return render(request, 'saints/inscription_list.html', context)


@login_required(login_url='/login/')
def edit_inscription(request, pk=None, focus='', view='complete'):
    """Allow adding a new or editing an existing [Saint] instance"""

    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "date_lower", "year_lower")
        partial_year_to_date(form, instance, "date_upper", "year_upper")

    names = 'inscriptionsaint_formset,inscriptionchurch_formset,inscriptionlink_formset'
    return edit_model(request, __name__, 'Inscription', 'saints', pk, formset_names=names,
                      focus=focus, view=view, before_save=before_save)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InscriptionUpdateView(UpdateView):
    model = Inscription
    fields = '__all__'
    success_url = reverse_lazy('saints:inscription-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InscriptionDeleteView(DeleteView):
    model = Inscription
    success_url = reverse_lazy("saints:inscription-list")


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InscriptionDetailView(DetailView):
    model = Inscription

# Er is toch iets wat ik niet begrijp met de locaties, waarom zie ik als ik bij 
# Inscriptions filter op ICERV307 (2 records, één is gekoppeld aan city 181, Guadix) ik veel meer locaties gekoppeld aan inscriptions zie
# en allerlei cities en churches

# Ok, het lijkt wel goed te werken als ik zoek naar Hilarius bij Saints, dan 1 resultaat en 1 city
# Heeft het dan toch te maken met de methode bij Saint? worden daar de dubbele uitgehaald?


# Saint
@login_required(login_url='/login/')
def SaintList(request):
    query_set = saintsimplesearch(request, 'saints', 'saint') # Hier komt het request vanaf utilities/views.py  
    query = request.GET.get("q", "")
    # query_set = Installation.objects.all()
    # if query is not None:
    #     query_set = query_set.filter(name__icontains=query)
         
    lst_saint = saintsimplesearch(request, 'saints', 'saint').values("death_city__id", 
            "saintchurchrelation__church__city__id",
            "saintinscriptionrelation__inscription__original_location_city__id", 
            "saintlitmanuscriptrelation__liturgical_manuscript__original_location_city__id"
            )
    # this results in a queryset of saints - but not of cities
    
    lst_city = [] # Hier komen id's mee
    # Wat gebeurt hier precies? Wat wordt doorgegeven?
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
    city_count = len(lst_city) # Waar gaat dit naartoe?       

    context = {'saint_list': query_set,
               'nentries': len(query_set), 
               'lentries': city_count,
               'query': query}

    return render(request, 'saints/saint_list.html', context)


@login_required(login_url='/login/')
def edit_saint(request, pk=None, focus='', view='complete'):
    """Allow adding a new or editing an existing [Saint] instance"""

    def before_save(form, instance):
        # Check for death_year vs death_date
        partial_year_to_date(form, instance, "death_date", "death_year")
        # Check for death_year vs death_date
        partial_year_to_date(form, instance, "death_date_last", "death_year_last")

    names = 'saintchurch_formset,saintinscription_formset,saintobject_formset,saintliturgicalmanuscript_formset,saintlink_formset'
    return edit_model(request, __name__, 'Saint', 'saints', pk, formset_names=names,
                      focus=focus, view=view, before_save=before_save)


@login_required(login_url='/login/')
class SaintUpdateView(UpdateView):
    model = Saint
    fields = '__all__'
    success_url = reverse_lazy('saints:saint-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SaintDeleteView(DeleteView):
    model = Saint
    success_url = reverse_lazy("saints:saint-list")


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SaintDetailView(DetailView):
    model = Saint


# LiteraryText
@login_required(login_url='/login/')
def LiteraryTextList(request):
    query_set = ltextsimplesearch(request, 'saints', 'literarytext')
    query = request.GET.get("q", "")
    context = {'ltext_list': query_set,
               'nentries': len(query_set),
               'query': query}
    return render(request, 'saints/literarytext_list.html', context)


@login_required(login_url='/login/')
def edit_ltext(request, pk=None, focus='', view='complete'):
    """Allow adding a new or editing an existing [Saint] instance"""

    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "date_lower", "year_lower")
        partial_year_to_date(form, instance, "date_upper", "year_upper")

    names = 'literarytextbibliography_formset,literarytextlink_formset' # 'ltextchurch_formset'
    return edit_model(request, __name__, 'LiteraryText', 'saints', pk, formset_names=names,
                      focus=focus, view=view, before_save=before_save)


@login_required(login_url='/login/')
class LiteraryTextUpdateView(UpdateView):
    model = LiteraryText
    fields = '__all__'
    success_url = reverse_lazy('saints:literarytext-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiteraryTextDeleteView(DeleteView):
    model = LiteraryText
    success_url = reverse_lazy("saints:literarytext-list")


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiteraryTextDetailView(DetailView):
    model = LiteraryText


# Object
@login_required(login_url='/login/')
def ObjectList(request):
    query_set = objectsimplesearch(request, 'saints', 'object')
    query = request.GET.get("q", "")
    
    # Probleem is dat de objecten niet gelinked zijn aan cities
    lst_object = objectsimplesearch(request, 'saints', 'object').values("original_location_city__id")

    list_cities=[] # Hier komen de id's in
    for oObject in lst_object:
        #print("this works")
        # dit moet anders, ID's meegeven, dit werkt
        city_object = oObject.get("city__id")
        # Wat doet dit?
        if not city_object is None and not city_object in lst_object: # Haalt er eventuele dubbele eruit.
            list_cities.append(city_church)
        # moet nog gefilterd worden, alleen churches doorsturen
        #list_church.append(oChurch)
    # Zitten er teveel in, hoe kan dat? Lijkt verdubbeling.
    # We krijgen de hele tijd de input van Saints...
    city_count = len(list_cities)
       
    
    context = {'object_list': query_set,
               'nentries': len(query_set),
               'lentries': city_count,
               'query': query}
    return render(request, 'saints/object_list.html', context)


@login_required(login_url='/login/')
def edit_object(request, pk=None, focus='', view='complete'):
    """Allow adding a new or editing an existing [Saint] instance"""

    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "date_lower", "year_lower")
        partial_year_to_date(form, instance, "date_upper", "year_upper")

    names = 'objectsaint_formset,objectchurch_formset,objectlink_formset'
    return edit_model(request, __name__, 'Object', 'saints', pk, formset_names=names,
                      focus=focus, view=view, before_save=before_save)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectUpdateView(UpdateView):
    model = Object
    fields = '__all__'
    success_url = reverse_lazy('saints:object-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectDeleteView(DeleteView):
    model = Object
    success_url = reverse_lazy("saints:object-list")


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectDetailView(DetailView):
    model = Object


# Feast
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class FeastListView(ListView):
    model = Feast
    template_name = 'installations/feast_list.html'
    context_object_name = 'feasts'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class FeastCreatView(CreateView):
    model = Feast
    fields = '__all__'
    template_name = 'saints/feast_form.html'
    success_url = reverse_lazy('saints:feast-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class FeastUpdateView(UpdateView):
    model = Feast
    fields = '__all__'
    success_url = reverse_lazy('saints:feast-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class FeastDeleteView(DeleteView):
    model = Feast
    success_url = reverse_lazy("saints:feast-list")


# AuthorAncient
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class AuthorAncientListView(ListView):
    model = AuthorAncient
    template_name = 'installations/authorancient_list.html'
    context_object_name = 'ancientauthors'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class AuthorAncientCreatView(CreateView):
    model = AuthorAncient
    fields = '__all__'
    template_name = 'saints/authorancient_form.html'
    success_url = reverse_lazy('saints:authorancient-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class AuthorAncientUpdateView(UpdateView):
    model = AuthorAncient
    fields = '__all__'
    success_url = reverse_lazy('saints:authorancient-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class AuthorAncientDeleteView(DeleteView):
    model = AuthorAncient
    success_url = reverse_lazy("saints:authorancient-list")


# LiturgicalManuscript

# @method_decorator(login_required(login_url='/login/'), name='dispatch')
# class LiturgicalManuscriptListView(ListView):
#     model = LiturgicalManuscript
#     template_name = 'installations/liturgicalmanuscript_list.html'
#     context_object_name = 'liturgicalmanuscripts'


@login_required(login_url='/login/')
def LiturgicalManuscriptList(request):
    query_set = liturgicalmanuscriptsimplesearch(request, 'saints', 'liturgicalmanuscript')
    query = request.GET.get("q", "")
    context = {'liturgicalmanuscript_list': query_set,
               'nentries': len(query_set),
               'query': query}
    return render(request, 'saints/liturgicalmanuscript_list.html', context)


@login_required(login_url='/login/')
def edit_liturgicalmanuscript(request, pk=None, focus='', view='complete'):
    """Allow adding a new or editing an existing [Saint] instance"""

    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "date_lower", "year_lower")
        partial_year_to_date(form, instance, "date_upper", "year_upper")

    names = 'liturgicalmanuscriptsaint_formset,liturgicalmanuscriptchurch_formset,litmanuscriptlink_formset'
    return edit_model(request, __name__, 'LiturgicalManuscript', 'saints', pk, formset_names=names,
                      focus=focus, view=view, before_save=before_save)


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalManuscriptUpdateView(UpdateView):
    model = LiturgicalManuscript
    fields = '__all__'
    success_url = reverse_lazy('saints:liturgicalmanuscript-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalManuscriptDeleteView(DeleteView):
    model = LiturgicalManuscript
    success_url = reverse_lazy("saints:liturgicalmanuscript-list")


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalManuscriptDetailView(DetailView):
    model = LiturgicalManuscript


# Rite
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RiteListView(ListView):
    model = Rite
    template_name = 'installations/rite_list.html'
    context_object_name = 'rites'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RiteCreatView(CreateView):
    model = Rite
    fields = '__all__'
    template_name = 'saints/rite_form.html'
    success_url = reverse_lazy('saints:rite-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RiteUpdateView(UpdateView):
    model = Rite
    fields = '__all__'
    success_url = reverse_lazy('saints:rite-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RiteDeleteView(DeleteView):
    model = Rite
    success_url = reverse_lazy("saints:rite-list")


# ManuscriptType
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ManuscriptTypeListView(ListView):
    model = ManuscriptType
    template_name = 'installations/manuscripttype_list.html'
    context_object_name = 'manuscripttypes'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ManuscriptTypeCreatView(CreateView):
    model = ManuscriptType
    fields = '__all__'
    template_name = 'saints/manuscripttype_form.html'
    success_url = reverse_lazy('saints:manuscripttype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ManuscriptTypeUpdateView(UpdateView):
    model = ManuscriptType
    fields = '__all__'
    success_url = reverse_lazy('saints:manuscripttype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ManuscriptTypeDeleteView(DeleteView):
    model = ManuscriptType
    success_url = reverse_lazy("saints:manuscripttype-list")


# ObjectType
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectTypeListView(ListView):
    model = ObjectType
    template_name = 'installations/objecttype_list.html'
    context_object_name = 'objecttypes'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectTypeCreatView(CreateView):
    model = ObjectType
    fields = '__all__'
    template_name = 'saints/objecttype_form.html'
    success_url = reverse_lazy('saints:objecttype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectTypeUpdateView(UpdateView):
    model = ObjectType
    fields = '__all__'
    success_url = reverse_lazy('saints:objecttype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class ObjectTypeDeleteView(DeleteView):
    model = ObjectType
    success_url = reverse_lazy("saints:objecttype-list")


# SaintType
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SaintTypeListView(ListView):
    model = SaintType
    template_name = 'installations/sainttype_list.html'
    context_object_name = 'sainttypes'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SaintTypeCreatView(CreateView):
    model = SaintType
    fields = '__all__'
    template_name = 'saints/sainttype_form.html'
    success_url = reverse_lazy('saints:sainttype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SaintTypeUpdateView(UpdateView):
    model = SaintType
    fields = '__all__'
    success_url = reverse_lazy('saints:sainttype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class SaintTypeDeleteView(DeleteView):
    model = SaintType
    success_url = reverse_lazy("saints:sainttype-list")


# LiturgicalType
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalTypeListView(ListView):
    model = LiturgicalType
    template_name = 'installations/liturgicaltype_list.html'
    context_object_name = 'liturgicaltypes'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalTypeCreatView(CreateView):
    model = LiturgicalType
    fields = '__all__'
    template_name = 'saints/liturgicaltype_form.html'
    success_url = reverse_lazy('saints:liturgicaltype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalTypeUpdateView(UpdateView):
    model = LiturgicalType
    fields = '__all__'
    success_url = reverse_lazy('saints:liturgicaltype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class LiturgicalTypeDeleteView(DeleteView):
    model = LiturgicalType
    success_url = reverse_lazy("saints:liturgicaltype-list")


# InstitutionType
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InstitutionTypeListView(ListView):
    model = InstitutionType
    template_name = 'installations/institutiontype_list.html'
    context_object_name = 'institutiontypes'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InstitutionTypeCreatView(CreateView):
    model = InstitutionType
    fields = '__all__'
    template_name = 'saints/institutiontype_form.html'
    success_url = reverse_lazy('saints:institutiontype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InstitutionTypeUpdateView(UpdateView):
    model = InstitutionType
    fields = '__all__'
    success_url = reverse_lazy('saints:institutiontype-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class InstitutionTypeDeleteView(DeleteView):
    model = InstitutionType
    success_url = reverse_lazy("saints:institutiontype-list")


# City
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class CityListView(ListView):
    model = City
    template_name = 'installations/city_list.html'
    context_object_name = 'city_list'

    def get_queryset(self):
        qs = City.objects.all().order_by('name')
        return qs


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class CityCreatView(CreateView):
    model = City
    fields = '__all__'
    template_name = 'saints/city_form.html'
    success_url = reverse_lazy('saints:city-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class CityDetailView(DetailView):
    model = City


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class CityUpdateView(UpdateView):
    model = City
    fields = '__all__'
    success_url = reverse_lazy('saints:city-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class CityDeleteView(DeleteView):
    model = City
    success_url = reverse_lazy("saints:city-list")


# Region
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RegionListView(ListView):
    model = Region
    template_name = 'installations/region_list.html'
    context_object_name = 'region_list'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RegionCreatView(CreateView):
    model = Region
    fields = '__all__'
    template_name = 'saints/region_form.html'
    success_url = reverse_lazy('saints:region-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RegionUpdateView(UpdateView):
    model = Region
    fields = '__all__'
    success_url = reverse_lazy('saints:region-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class RegionDeleteView(DeleteView):
    model = Region
    success_url = reverse_lazy("saints:region-list")


# Museum
@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MuseumListView(ListView):
    model = Museum
    template_name = 'installations/museum_list.html'
    context_object_name = 'museum_list'


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MuseumCreatView(CreateView):
    model = Museum
    fields = '__all__'
    template_name = 'saints/museum_form.html'
    success_url = reverse_lazy('saints:museum-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MuseumUpdateView(UpdateView):
    model = Museum
    fields = '__all__'
    success_url = reverse_lazy('saints:museum-list')


@method_decorator(login_required(login_url='/login/'), name='dispatch')
class MuseumDeleteView(DeleteView):
    model = Museum
    success_url = reverse_lazy("saints:museum-list")