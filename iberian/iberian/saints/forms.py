from django.forms import ModelForm, inlineformset_factory
from django import forms

from crispy_forms.helper import FormHelper
from django_select2 import forms as s2forms

# ========== Imports from own application ========================================
from .models import *


DATA_MINIMUM_INPUT_LENGTH = 0

def partial_year_to_date(form, instance, date_field, year_field):
    """Used in [before_save()] to change the date_field"""

    # Get the value of the year_field
    value_year = form.cleaned_data.get(year_field)
    if value_year != "":
        value_year = value_year.zfill(4)
    # Get the date_field
    value_date = getattr(instance, date_field)
    # If they are the same: don't change
    if value_date != value_year:
        # Check for changes
        if value_date is None or value_date == "" or str(value_date.date.year).zfill(4) != value_year:
            # Adapt the form's instance value
            setattr(form.instance, date_field, value_year)



# ============================ Widgets ============================================
class SaintTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = SaintType.objects.all().order_by('name')
        return qs


class LiturgicalTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = LiturgicalType.objects.all().order_by('name')
        return qs


class SaintWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = Saint.objects.all().order_by('name')
        return qs


class LiteraryTextWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = LiteraryText.objects.all().order_by('name')
        return qs


class ChurchWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = Church.objects.all().order_by('name')
        return qs


class CityWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = City.objects.all().order_by('name')
        return qs


class RegionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['city__name__icontains',
                     'region_number__icontains', ]

    def get_queryset(self):
        qs = Region.objects.all().order_by('city__name', 'region_number')
        return qs


class MuseumWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = Museum.objects.all().order_by('name')
        return qs


class InscriptionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['reference_no__icontains']

    def get_queryset(self):
        qs = Inscription.objects.all().order_by('reference_no')
        return qs


class ObjectWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = Object.objects.all().order_by('name')
        return qs


class ObjectTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = ObjectType.objects.all().order_by('name')
        return qs


class LiturgicalManuscriptWidget(s2forms.ModelSelect2Widget):
    search_fields = ['shelf_no__icontains']

    def get_queryset(self):
        qs = LiturgicalManuscript.objects.all().order_by('shelf_no')
        return qs


class InstitutionTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = InstitutionType.objects.all().order_by('name')
        return qs


class RiteWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = Rite.objects.all().order_by('name')
        return qs


class FeastWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = Feast.objects.all().order_by('name')
        return qs


class AuthorAncientWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = AuthorAncient.objects.all().order_by('name')
        return qs


class ManuscriptTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']

    def get_queryset(self):
        qs = ManuscriptType.objects.all().order_by('name')
        return qs


class BibliographyWidget(s2forms.ModelSelect2Widget):
    search_fields = ['short_title__icontains']

    def get_queryset(self):
        qs = Bibliography.objects.all().order_by('short_title')
        return qs


class BibliographyWidgetMulti(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'short_title__icontains',
        'author__icontains',
    ]

    def get_queryset(self):
        qs = Bibliography.objects.all().order_by('short_title', 'author')
        return qs


# ==================== User form ==============================
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')


class UserPasswordChangeForm(forms.Form):
    password_old = forms.CharField(widget=forms.PasswordInput())
    password_new = forms.CharField(widget=forms.PasswordInput())
    password_new2 = forms.CharField(widget=forms.PasswordInput())

    #class Meta():
    #    model = User
    #    fields = ('password', 'password_new', 'password_new2')


class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        # fields = ('portfolio_site', 'profile_pic')
        fields = ()


# ================ Location forms: City, Region, Museum, Church as a location =========================
class CityForm(ModelForm):
    class Meta:
        model = City
        fields = ['name', 'latitude', 'longitude']
        labels = {
            'name': 'City Name'
        }

    def __init__(self, *args, **kwargs):
        super(CityForm, self).__init__(*args, **kwargs)
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.helper = FormHelper()


class RegionForms(ModelForm):
    extent_shapefile = forms.FileField(widget=forms.ClearableFileInput)

    class Meta:
        model = Region
        fields = ('city', 'region_number', 'extent_shapefile')


class MuseumForms(ModelForm):
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)

    class Meta:
        model = Museum
        fields = ('name', 'city', 'description')


# ================= Other Forms =======================================================================
class SaintForm(forms.ModelForm):

    # Add a separate input for the YEAR
    death_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = Saint
        fields = '__all__'

    type = forms.ModelChoiceField(
        queryset=SaintType.objects.all().order_by('name'),
        # this line refreshes the list when a new item is entered using the plus button
        widget=SaintTypeWidget(
            attrs={'data-placeholder': 'Select saint type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    ltype = forms.ModelChoiceField(
        queryset=LiturgicalType.objects.all().order_by('name'),
        # this line refreshes the list when a new item is entered using the plus button
        widget=LiturgicalTypeWidget(
            attrs={'data-placeholder': 'Select liturgical type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    location_region = forms.ModelChoiceField(required=False, queryset=Region.objects.all(), widget=RegionWidget(
        attrs={'data-placeholder': 'Select Region','style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))

    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)

    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(SaintForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['type'].required = False
        self.fields['ltype'].required = False
        self.fields['status'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the death_year
            if not instance.death_date is None:
                # This is just collecting what we have
                death_year = str(instance.death_date.date.year)
                self.fields['death_year'].initial = death_year


class ChurchForm(ModelForm):

    # Add a separate input for the YEAR
    year_lower = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    year_upper = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = Church
        fields = '__all__'
        labels = {
            'name': 'Church Name'
        }

    date_lower = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter lower bound'}))
    date_upper = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter upper bound'}))

    coordinates_latitude = forms.DecimalField(widget=forms.TextInput(attrs={'placeholder': 'Latitude'}), required=False)
    coordinates_longitude = forms.DecimalField(widget=forms.TextInput(attrs={'placeholder': 'Longitude'}),
                                               required=False)
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    institution_type = forms.ModelChoiceField(
        queryset=InstitutionType.objects.all(),
        # this line refreshes the list when a new item is entered using the plus button
        widget=InstitutionTypeWidget(
            attrs={'data-placeholder': 'Select institution type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    #
    # bibliography = forms.ModelChoiceField(
    #     queryset=Bibliography.objects.all(),
    #     # this line refreshes the list when a new item is entered using the plus button
    #     widget=BibliographyWidget(
    #         attrs={'data-placeholder': 'Select bibliography',
    #                'style': 'width:100%;', 'class': 'searching',
    #                'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    #     required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(ChurchForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True

        self.fields['date_lower'].required = False
        self.fields['date_upper'].required = False
        self.fields['status'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the date_lower
            if not instance.date_lower is None:
                # This is just collecting what we have
                self.fields['year_lower'].initial = str(instance.date_lower.date.year)
            # Fill in the correct value for the date_upper
            if not instance.date_upper is None:
                # This is just collecting what we have
                self.fields['year_upper'].initial = str(instance.date_upper.date.year)


class ObjectForm(ModelForm):

    # Add a separate input for the YEAR
    year_lower = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    year_upper = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = Object
        fields = '__all__'

    date_lower = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter lower bound'}))
    date_upper = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter upper bound'}))
    original_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    original_location_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    original_location_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    current_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    current_location_museum = forms.ModelChoiceField(
        queryset=Museum.objects.all(),
        widget=MuseumWidget(
            attrs={'data-placeholder': 'Select Museum',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    type = forms.ModelChoiceField(
        queryset=ObjectType.objects.all().order_by('name'),
        widget=ObjectTypeWidget(
            attrs={'data-placeholder': 'Select object type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    bibliography = forms.ModelChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(
            attrs={'data-placeholder': 'Select bibliography',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(ObjectForm, self).__init__(*args, **kwargs)
        self.fields['date_lower'].required = False
        self.fields['date_upper'].required = False
        self.fields['status'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the date_lower
            if not instance.date_lower is None:
                # This is just collecting what we have
                self.fields['year_lower'].initial = str(instance.date_lower.date.year)
            # Fill in the correct value for the date_upper
            if not instance.date_upper is None:
                # This is just collecting what we have
                self.fields['year_upper'].initial = str(instance.date_upper.date.year)


class InscriptionForm(ModelForm):

    # Add a separate input for the YEAR
    year_lower = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    year_upper = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = Inscription
        fields = '__all__'

    date_lower = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter lower bound'}))
    date_upper = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter upper bound'}))

    original_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    original_location_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    original_location_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    current_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    current_location_museum = forms.ModelChoiceField(
        queryset=Museum.objects.all(),
        widget=MuseumWidget(
            attrs={'data-placeholder': 'Select Museum',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    bibliography = forms.ModelChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(
            attrs={'data-placeholder': 'Select bibliography',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    text = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(InscriptionForm, self).__init__(*args, **kwargs)
        self.fields['date_lower'].required = False
        self.fields['date_upper'].required = False
        self.fields['status'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the date_lower
            if not instance.date_lower is None:
                # This is just collecting what we have
                self.fields['year_lower'].initial = str(instance.date_lower.date.year)
            # Fill in the correct value for the date_upper
            if not instance.date_upper is None:
                # This is just collecting what we have
                self.fields['year_upper'].initial = str(instance.date_upper.date.year)


class LiteraryTextForm(ModelForm):
    """A literary text is the assumed original of a text that later occurs in manuscripts."""

    # Add a separate input for the YEAR
    year_lower = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    year_upper = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = LiteraryText
        fields = '__all__'

    date_lower = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter lower bound'}))
    date_upper = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter upper bound'}))

    # Location form fields
    location_city = forms.ModelChoiceField(required=False, queryset=None, widget=CityWidget( 
        attrs={'data-placeholder': 'Select City', 'style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))
    location_region = forms.ModelChoiceField(required=False, queryset=None, widget=RegionWidget(
        attrs={'data-placeholder': 'Select Region','style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))
    location_church = forms.ModelChoiceField(required=False, queryset=None, widget=ChurchWidget(
        attrs={'data-placeholder': 'Select Church','style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))
    location_museum = forms.ModelChoiceField(required=False, queryset=None, widget=MuseumWidget(
        attrs={'data-placeholder': 'Select Museum','style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))

    author = forms.ModelChoiceField(required=False, queryset=None, widget=AuthorAncientWidget(
        attrs={'data-placeholder': 'Select Author','style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))
    bibliography_many = forms.ModelMultipleChoiceField(required=False, queryset=None, widget=BibliographyWidgetMulti(
        attrs={'data-placeholder': '','style': 'width:100%;', 'class': 'searching', 'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}))

    # Text and other fields
    text = forms.CharField(widget=forms.Textarea( attrs={'style': 'width:100%', 'rows': 3}), required=False)
    description = forms.CharField(widget=forms.Textarea( attrs={'style': 'width:100%', 'rows': 3}), required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        # First perform the default thing
        super(LiteraryTextForm, self).__init__(*args, **kwargs)
        # Make sure some fields are not perceived as obligatory
        self.fields['date_lower'].required = False
        self.fields['date_upper'].required = False
        self.fields['status'].required = False

        # Initialize the querysets of the fields
        self.fields['location_city'].queryset = City.objects.all()
        self.fields['location_region'].queryset = Region.objects.all()
        self.fields['location_church'].queryset = Church.objects.all()
        self.fields['location_museum'].queryset = Museum.objects.all()
        self.fields['author'].queryset = AuthorAncient.objects.all()
        self.fields['bibliography_many'].queryset = Bibliography.objects.all()

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the date_lower
            if not instance.date_lower is None:
                # This is just collecting what we have
                self.fields['year_lower'].initial = str(instance.date_lower.date.year)
            # Fill in the correct value for the date_upper
            if not instance.date_upper is None:
                # This is just collecting what we have
                self.fields['year_upper'].initial = str(instance.date_upper.date.year)


class LiturgicalManuscriptForm(ModelForm):

    # Add a separate input for the YEAR
    year_lower = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    year_upper = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = LiturgicalManuscript
        fields = '__all__'

    date_lower = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter lower bound'}))
    date_upper = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Please enter upper bound'}))

    rite = forms.ModelChoiceField(
        queryset=Rite.objects.all(),
        widget=RiteWidget(
            attrs={'data-placeholder': 'Select rite',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    type = forms.ModelChoiceField(
        queryset=ManuscriptType.objects.all(),
        widget=ManuscriptTypeWidget(
            attrs={'data-placeholder': 'Select manuscript type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    original_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    original_location_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    original_location_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    provenance = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    provenance_museum = forms.ModelChoiceField(
        queryset=Museum.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Museum',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    feast = forms.ModelChoiceField(
        queryset=Rite.objects.all(),
        widget=FeastWidget(
            attrs={'data-placeholder': 'Select feast',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)

    bibliography = forms.ModelChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(
            attrs={'data-placeholder': 'Select bibliography',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
        required=False)
    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)
    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(LiturgicalManuscriptForm, self).__init__(*args, **kwargs)
        self.fields['date_lower'].required = False
        self.fields['date_upper'].required = False
        self.fields['status'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the date_lower
            if not instance.date_lower is None:
                # This is just collecting what we have
                self.fields['year_lower'].initial = str(instance.date_lower.date.year)
            # Fill in the correct value for the date_upper
            if not instance.date_upper is None:
                # This is just collecting what we have
                self.fields['year_upper'].initial = str(instance.date_upper.date.year)


class BibliographyForm(ModelForm):
    # Add a separate input for the YEAR
    char_year = forms.CharField(label="Year", required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    class Meta:
        model = Bibliography
        fields = '__all__'
        exclude = ("year",)
        # its possible to use following line for all fields, also exclude
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BibliographyForm, self).__init__(*args, **kwargs)

        # self.fields['year'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the death_year
            if not instance.year is None:
                # This is just collecting what we have
                self.fields['char_year'].initial = str(instance.year.date.year)


class InstitutionTypeForm(ModelForm):
    class Meta:
        model = InstitutionType
        fields = '__all__'


# ========================== Relations form ===========================================================
class SaintChurchRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = SaintChurchRelation
        fields = ('saint', 'church')


class SaintInscriptionRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )
    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all(),
        widget=InscriptionWidget(
            attrs={'data-placeholder': 'Select inscription',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = SaintInscriptionRelation
        fields = ('saint', 'inscription')


class SaintObjectRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    object = forms.ModelChoiceField(
        queryset=Object.objects.all(),
        widget=ObjectWidget(
            attrs={'data-placeholder': 'Select object',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = SaintObjectRelation
        fields = ('saint', 'object')


class SaintLitManuscriptRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    liturgical_manuscript = forms.ModelChoiceField(
        queryset=LiturgicalManuscript.objects.all(),
        widget=LiturgicalManuscriptWidget(
            attrs={'data-placeholder': 'Select liturgical manuscript',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = SaintLitManuscriptRelation
        fields = ('saint', 'liturgical_manuscript')


class ChurchObjectRelationForm(ModelForm):

    # Add a separate input for the YEAR
    start_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    end_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    object = forms.ModelChoiceField(
        queryset=Object.objects.all(),
        widget=ObjectWidget(
            attrs={'data-placeholder': 'Select object',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = ObjectChurchRelation
        fields = ('church', 'object', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super(ChurchObjectRelationForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the start_date
            if not instance.start_date is None:
                # This is just collecting what we have
                self.fields['start_year'].initial = str(instance.start_date.date.year)
            # Fill in the correct value for the end_date
            if not instance.end_date is None:
                # This is just collecting what we have
                self.fields['end_year'].initial = str(instance.end_date.date.year)

    def save(self, commit=True, *args, **kwargs):
        # Get the instance
        instance = self.instance
        # Adapt the form.instance for start_date and end_date
        partial_year_to_date(self, instance, "start_date", "start_year")
        partial_year_to_date(self, instance, "end_date", "end_year")
        # Perform the actual saving
        response = super(ChurchObjectRelationForm, self).save(commit=commit)
        # Return the save response
        return response


class ChurchLitManuscriptRelationForm(ModelForm):

    # Add a separate input for the YEAR
    start_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    end_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    liturgical_manuscript = forms.ModelChoiceField(
        queryset=LiturgicalManuscript.objects.all(),
        widget=LiturgicalManuscriptWidget(
            attrs={'data-placeholder': 'Select liturgical manuscript',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = LitManuscriptChurchRelation
        fields = ('church', 'liturgical_manuscript', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super(ChurchLitManuscriptRelationForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the start_date
            if not instance.start_date is None:
                # This is just collecting what we have
                self.fields['start_year'].initial = str(instance.start_date.date.year)
            # Fill in the correct value for the end_date
            if not instance.end_date is None:
                # This is just collecting what we have
                self.fields['end_year'].initial = str(instance.end_date.date.year)

    def save(self, commit=True, *args, **kwargs):
        #instance = kwargs.get("instance")
        instance = self.instance
        partial_year_to_date(self, instance, "start_date", "start_year")
        partial_year_to_date(self, instance, "end_date", "end_year")
        # Perform the actual saving
        response = super(ChurchLitManuscriptRelationForm, self).save(commit=commit)
        # Return the save response
        return response


class InscriptionChurchRelationForm(ModelForm):

    # Add a separate input for the YEAR
    start_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))
    end_year = forms.CharField(required=False,widget=forms.TextInput(attrs={'placeholder': 'Please enter a year'}))

    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all(),
        widget=InscriptionWidget(
            attrs={'data-placeholder': 'Select inscription',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = InscriptionChurchRelation
        fields = ('church', 'inscription', 'start_date', 'end_date')

    def __init__(self, *args, **kwargs):
        super(InscriptionChurchRelationForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False

        # Check if the instance is there
        instance = kwargs.get("instance")
        if not instance is None:
            # Fill in the correct value for the start_date
            if not instance.start_date is None:
                # This is just collecting what we have
                self.fields['start_year'].initial = str(instance.start_date.date.year)
            # Fill in the correct value for the end_date
            if not instance.end_date is None:
                # This is just collecting what we have
                self.fields['end_year'].initial = str(instance.end_date.date.year)

    def save(self, commit=True, *args, **kwargs):
        #instance = kwargs.get("instance")
        instance = self.instance
        partial_year_to_date(self, instance, "start_date", "start_year")
        partial_year_to_date(self, instance, "end_date", "end_year")
        # Perform the actual saving
        response = super(InscriptionChurchRelationForm, self).save(commit=commit)
        # Return the save response
        return response



# ================================== Multiple Links ==========================================
class SaintLinkRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = SaintLinkRelation
        fields = ('saint', 'link')


class ChurchLinkRelationForm(ModelForm):
    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = ChurchLinkRelation
        fields = ('church', 'link')


class ObjectLinkRelationForm(ModelForm):
    object = forms.ModelChoiceField(
        queryset=Object.objects.all(),
        widget=ObjectWidget(
            attrs={'data-placeholder': 'Select object',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = ObjectLinkRelation
        fields = ('object', 'link')


class InscriptionLinkRelationForm(ModelForm):
    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all(),
        widget=InscriptionWidget(
            attrs={'data-placeholder': 'Select inscription',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = InscriptionLinkRelation
        fields = ('inscription', 'link')


class LitManuscriptLinkRelationForm(ModelForm):
    liturgical_manuscript = forms.ModelChoiceField(
        queryset=LiturgicalManuscript.objects.all(),
        widget=LiturgicalManuscriptWidget(
            attrs={'data-placeholder': 'Select liturgical manuscript',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = LitManuscriptLinkRelation
        fields = ('liturgical_manuscript', 'link')


class LiteraryTextLinkRelationForm(ModelForm):
    ltext = forms.ModelChoiceField(queryset=LiteraryText.objects.all(),
        widget=LiteraryTextWidget(attrs={'data-placeholder': 'Select literary text',
            'style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = LiteraryTextLinkRelation
        fields = ('ltext', 'link')


class LiteraryTextBibliographyRelationForm(ModelForm):
    ltext = forms.ModelChoiceField( queryset=LiteraryText.objects.all(),
        widget=LiteraryTextWidget(attrs={'data-placeholder': 'Select literary text',
            'style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )
    bibliography = forms.ModelChoiceField( queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(attrs={'data-placeholder': 'Select bibliography item',
            'style': 'width:100%;', 'class': 'searching','data-minimum-input-length': DATA_MINIMUM_INPUT_LENGTH}),
    )

    class Meta:
        model = LiteraryTextBibliographyRelation
        fields = ('ltext', 'bibliography')


# ================================= Formsets ===============================================

saintchurch_formset = inlineformset_factory(
    Saint, SaintChurchRelation, form=SaintChurchRelationForm, extra=1)
churchsaint_formset = inlineformset_factory(
    Church, SaintChurchRelation, form=SaintChurchRelationForm, extra=1)

saintinscription_formset = inlineformset_factory(
    Saint, SaintInscriptionRelation, form=SaintInscriptionRelationForm, extra=1)
inscriptionsaint_formset = inlineformset_factory(
    Inscription, SaintInscriptionRelation, form=SaintInscriptionRelationForm, extra=1)

saintobject_formset = inlineformset_factory(
    Saint, SaintObjectRelation, form=SaintObjectRelationForm, extra=1)
objectsaint_formset = inlineformset_factory(
    Object, SaintObjectRelation, form=SaintObjectRelationForm, extra=1)

saintliturgicalmanuscript_formset = inlineformset_factory(
    Saint, SaintLitManuscriptRelation, form=SaintLitManuscriptRelationForm, extra=1)
liturgicalmanuscriptsaint_formset = inlineformset_factory(
    LiturgicalManuscript, SaintLitManuscriptRelation, form=SaintLitManuscriptRelationForm, extra=1)

churchobject_formset = inlineformset_factory(
    Church, ObjectChurchRelation, form=ChurchObjectRelationForm, extra=1)
objectchurch_formset = inlineformset_factory(
    Object, ObjectChurchRelation, form=ChurchObjectRelationForm, extra=1)

churchliturgicalmanuscript_formset = inlineformset_factory(
    Church, LitManuscriptChurchRelation, form=ChurchLitManuscriptRelationForm, extra=1)
liturgicalmanuscriptchurch_formset = inlineformset_factory(
    LiturgicalManuscript, LitManuscriptChurchRelation, form=ChurchLitManuscriptRelationForm, extra=1)

inscriptionchurch_formset = inlineformset_factory(
    Inscription, InscriptionChurchRelation, form=InscriptionChurchRelationForm, extra=1)
churchinscription_formset = inlineformset_factory(
    Church, InscriptionChurchRelation, form=InscriptionChurchRelationForm, extra=1)

# ================================== LiteraryText ============================================

#ltextchurch_formset = inlineformset_factory(LiteraryText, LiteraryTextChurchRelation,
#                                            form=LiteraryTextChurchRelationForm, extra=1)
#churchltext_formset = inlineformset_factory(Church, LiteraryTextChurchRelation,
#                                            form=LiteraryTextChurchRelationForm, extra=1)


# ================================== Multiple Links ==========================================
saintlink_formset = inlineformset_factory(
    Saint, SaintLinkRelation, form=SaintLinkRelationForm, extra=1)

churchlink_formset = inlineformset_factory(
    Church, ChurchLinkRelation, form=ChurchLinkRelationForm, extra=1)

objectlink_formset = inlineformset_factory(
    Object, ObjectLinkRelation, form=ObjectLinkRelationForm, extra=1)

inscriptionlink_formset = inlineformset_factory(
    Inscription, InscriptionLinkRelation, form=InscriptionLinkRelationForm, extra=1)

litmanuscriptlink_formset = inlineformset_factory(
    LiturgicalManuscript, LitManuscriptLinkRelation, form=LitManuscriptLinkRelationForm, extra=1)

literarytextlink_formset = inlineformset_factory(
    LiteraryText, LiteraryTextLinkRelation, form=LiteraryTextLinkRelationForm, extra=1)

literarytextbibliography_formset = inlineformset_factory(
    LiteraryText, LiteraryTextBibliographyRelation, form=LiteraryTextBibliographyRelationForm, extra=1)

