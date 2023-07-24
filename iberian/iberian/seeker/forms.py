"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.forms import ModelMultipleChoiceField, ModelChoiceField
from django.forms.widgets import *
from django.db.models import F, Case, Value, When, IntegerField
from django_select2.forms import ModelSelect2Mixin, Select2MultipleWidget, ModelSelect2MultipleWidget, ModelSelect2TagWidget, ModelSelect2Widget, HeavySelect2Widget
from django.contrib.auth.models import User, Group

from iberian.seeker.models import *
from iberian.basic.forms import BasicModelForm, BasicSimpleForm


# ================= WIDGETS =====================================


class UserWidget(ModelSelect2MultipleWidget):
    model = User
    search_fields = [ 'username__icontains' ]

    def label_from_instance(self, obj):
        return obj.username

    def get_queryset(self):
        return User.objects.all().order_by('username').distinct()



# ================= FORMS =======================================

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class UploadForm(BasicModelForm):
    """Details of an upload"""

    userlist   = ModelMultipleChoiceField(queryset=None, required=False,
                widget=UserWidget(attrs={'data-placeholder': 'Select multiple users...', 'style': 'width: 100%;', 'class': 'searching'}))

    class Meta:
        ATTRS_FOR_FORMS = {'class': 'form-control'};

        model = Upload
        fields = ['user', 'name', 'upfile']
        widgets={'name':    forms.TextInput(attrs={'style': 'width: 100%;', 'class': 'searching'}),
                 'upfile':  forms.FileInput(attrs={'style': 'width: 100%;', 'placeholder': 'File to be uploaded'}),
                 }

    def __init__(self, *args, **kwargs):
        # Start by executing the standard handling
        super(UploadForm, self).__init__(*args, **kwargs)

        oErr = ErrHandle()
        try:
            # Some fields are not required
            self.fields['user'].required = False
            self.fields['name'].required = False
            self.fields['upfile'].required = False

            self.fields['userlist'].queryset = User.objects.all().order_by('username')

            # Get the instance
            if 'instance' in kwargs:
                instance = kwargs['instance']

        except:
            msg = oErr.get_error_message()
            oErr.DoError("UploadForm-init")
        # We are okay
        return None
