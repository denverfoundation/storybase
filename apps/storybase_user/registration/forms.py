from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail

class ExtraInfoRegistrationForm(RegistrationFormUniqueEmail):
    # max_length is set to 61 which is the maximum length of the User model's
    # first_name field (30), plus a space, plus the maximum length of the User
    # model's last_name field (30)
    full_name = forms.CharField(max_length=61)
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
