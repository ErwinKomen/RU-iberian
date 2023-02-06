from django.forms import ModelForm, inlineformset_factory
from django import forms

from .models import *
from crispy_forms.helper import FormHelper
from django_select2 import forms as s2forms


# Widgets
class SaintTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class SaintWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class ChurchWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class CityWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class RegionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['city__name__icontains',
                     'region_number__icontains', ]


class MuseumWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class InscriptionWidget(s2forms.ModelSelect2Widget):
    search_fields = ['reference_no__icontains']


class ObjectWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class ObjectTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class LiturgicalManuscriptWidget(s2forms.ModelSelect2Widget):
    search_fields = ['shelf_no__icontains']


class InstitutionTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class RiteWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class FeastWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class ManuscriptTypeWidget(s2forms.ModelSelect2Widget):
    search_fields = ['name__icontains']


class BibliographyWidget(s2forms.ModelSelect2Widget):
    search_fields = ['short_title__icontains']


class BibliographyWidgetMulti(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'short_title__icontains',
        'author__icontains',
    ]


# User form
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')


class UserProfileInfoForm(forms.ModelForm):
    class Meta():
        model = UserProfileInfo
        # fields = ('portfolio_site', 'profile_pic')
        fields = ()


# Location forms: City, Region, Museum, Church as a location
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


# Forms
class SaintForm(forms.ModelForm):
    class Meta:
        model = Saint
        fields = '__all__'

    type = forms.ModelChoiceField(
        queryset=SaintType.objects.all().order_by('name'),
        # this line refreshes the list when a new item is entered using the plus button
        widget=SaintTypeWidget(
            attrs={'data-placeholder': 'Select saint type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)

    description = forms.CharField(widget=forms.Textarea(
        attrs={'style': 'width:100%', 'rows': 3}),
        required=False)

    status = forms.BooleanField()

    def __init__(self, *args, **kwargs):
        super(SaintForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['type'].required = False
        self.fields['status'].required = False


class ChurchForm(ModelForm):
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
                   'data-minimum-input-length': '1'}),
        required=False)
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    institution_type = forms.ModelChoiceField(
        queryset=InstitutionType.objects.all(),
        # this line refreshes the list when a new item is entered using the plus button
        widget=InstitutionTypeWidget(
            attrs={'data-placeholder': 'Select institution type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    #
    # bibliography = forms.ModelChoiceField(
    #     queryset=Bibliography.objects.all(),
    #     # this line refreshes the list when a new item is entered using the plus button
    #     widget=BibliographyWidget(
    #         attrs={'data-placeholder': 'Select bibliography',
    #                'style': 'width:100%;', 'class': 'searching',
    #                'data-minimum-input-length': '1'}),
    #     required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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


class ObjectForm(ModelForm):
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
                   'data-minimum-input-length': '1'}),
        required=False)
    original_location_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    original_location_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    current_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    current_location_museum = forms.ModelChoiceField(
        queryset=Museum.objects.all(),
        widget=MuseumWidget(
            attrs={'data-placeholder': 'Select Museum',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    type = forms.ModelChoiceField(
        queryset=ObjectType.objects.all().order_by('name'),
        widget=ObjectTypeWidget(
            attrs={'data-placeholder': 'Select object type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)

    bibliography = forms.ModelChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(
            attrs={'data-placeholder': 'Select bibliography',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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


class InscriptionForm(ModelForm):
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
                   'data-minimum-input-length': '1'}),
        required=False)
    original_location_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    original_location_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    current_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    current_location_museum = forms.ModelChoiceField(
        queryset=Museum.objects.all(),
        widget=MuseumWidget(
            attrs={'data-placeholder': 'Select Museum',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)

    bibliography = forms.ModelChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(
            attrs={'data-placeholder': 'Select bibliography',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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


class LiturgicalManuscriptForm(ModelForm):
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
                   'data-minimum-input-length': '1'}),
        required=False)
    type = forms.ModelChoiceField(
        queryset=ManuscriptType.objects.all(),
        widget=ManuscriptTypeWidget(
            attrs={'data-placeholder': 'Select manuscript type',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    original_location = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)

    original_location_city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=CityWidget(
            attrs={'data-placeholder': 'Select City',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    original_location_region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        widget=RegionWidget(
            attrs={'data-placeholder': 'Select Region',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    provenance = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    provenance_museum = forms.ModelChoiceField(
        queryset=Museum.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select Museum',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    feast = forms.ModelChoiceField(
        queryset=Rite.objects.all(),
        widget=FeastWidget(
            attrs={'data-placeholder': 'Select feast',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)

    bibliography = forms.ModelChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidget(
            attrs={'data-placeholder': 'Select bibliography',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
        required=False)
    bibliography_many = forms.ModelMultipleChoiceField(
        queryset=Bibliography.objects.all(),
        widget=BibliographyWidgetMulti(
            attrs={'data-placeholder': '',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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


class BibliographyForm(ModelForm):
    class Meta:
        model = Bibliography
        fields = '__all__'
        # its possible to use following line for all fields, also exclude
        # fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(BibliographyForm, self).__init__(*args, **kwargs)
        # self.fields['country'].empty_label = "Select"
        self.fields['year'].required = False


class InstitutionTypeForm(ModelForm):
    class Meta:
        model = InstitutionType
        fields = '__all__'


# Relations form
class SaintChurchRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
    )
    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all(),
        widget=InscriptionWidget(
            attrs={'data-placeholder': 'Select inscription',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
    )

    object = forms.ModelChoiceField(
        queryset=Object.objects.all(),
        widget=ObjectWidget(
            attrs={'data-placeholder': 'Select object',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
    )

    liturgical_manuscript = forms.ModelChoiceField(
        queryset=LiturgicalManuscript.objects.all(),
        widget=LiturgicalManuscriptWidget(
            attrs={'data-placeholder': 'Select liturgical manuscript',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    class Meta:
        model = SaintLitManuscriptRelation
        fields = ('saint', 'liturgical_manuscript')


class ChurchObjectRelationForm(ModelForm):
    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    object = forms.ModelChoiceField(
        queryset=Object.objects.all(),
        widget=ObjectWidget(
            attrs={'data-placeholder': 'Select object',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    class Meta:
        model = ObjectChurchRelation
        fields = ('church', 'object', 'start_date', 'end_date')


class ChurchLitManuscriptRelationForm(ModelForm):
    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    liturgical_manuscript = forms.ModelChoiceField(
        queryset=LiturgicalManuscript.objects.all(),
        widget=LiturgicalManuscriptWidget(
            attrs={'data-placeholder': 'Select liturgical manuscript',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    class Meta:
        model = LitManuscriptChurchRelation
        fields = ('church', 'liturgical_manuscript', 'start_date', 'end_date')


class InscriptionChurchRelationForm(ModelForm):
    church = forms.ModelChoiceField(
        queryset=Church.objects.all(),
        widget=ChurchWidget(
            attrs={'data-placeholder': 'Select church',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    inscription = forms.ModelChoiceField(
        queryset=Inscription.objects.all(),
        widget=InscriptionWidget(
            attrs={'data-placeholder': 'Select inscription',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
    )

    class Meta:
        model = InscriptionChurchRelation
        fields = ('church', 'inscription', 'start_date', 'end_date')


# Multiple Links
class SaintLinkRelationForm(ModelForm):
    saint = forms.ModelChoiceField(
        queryset=Saint.objects.all(),
        widget=SaintWidget(
            attrs={'data-placeholder': 'Select saint',
                   'style': 'width:100%;', 'class': 'searching',
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
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
                   'data-minimum-input-length': '1'}),
    )

    class Meta:
        model = LitManuscriptLinkRelation
        fields = ('liturgical_manuscript', 'link')
# Formsets

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

# Multiple Links
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