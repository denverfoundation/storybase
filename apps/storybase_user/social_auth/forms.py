"""Custom forms for authentication and registration"""
from django import forms
from django.utils.translation import ugettext_lazy as _

# TODO: See if this can be merged with 
# storybase_user.registration.forms.ExtraInfoRegistrationForm
class TosForm(forms.Form):
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
        label=_(u'I have read and agree to the Terms of Service'),
        error_messages={
            'required': _("You must agree to the terms to register")
        })

class EmailTosForm(TosForm):
    email = forms.EmailField()
