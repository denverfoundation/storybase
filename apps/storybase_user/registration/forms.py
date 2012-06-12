from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail

# Based on django-email-usernames by Hakan Waara
# https://bitbucket.org/hakanw/django-email-usernames
class EmailUsernameRegistrationForm(RegistrationFormUniqueEmail):
    """Registration form that uses the user's email address for the username"""
    def __init__(self, *args, **kwargs):
        super(EmailUsernameRegistrationForm, self).__init__(*args, **kwargs)
        # Remove the username field
        del self.fields['username']

    def clean_email(self):
        """
        Validates email address is unique and sets username field to email 
        """
        email = super(EmailUsernameRegistrationForm, self).clean_email()
        self.cleaned_data['username'] = email
        return email


class ExtraInfoRegistrationForm(EmailUsernameRegistrationForm):
    # max_length is set to 61 which is the maximum length of the User model's
    # first_name field (30), plus a space, plus the maximum length of the User
    # model's last_name field (30)
    full_name = forms.CharField(max_length=61)
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})
