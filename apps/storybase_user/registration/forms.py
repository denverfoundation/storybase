from django import forms
from django.utils.translation import ugettext_lazy as _

from registration.forms import RegistrationFormUniqueEmail

# Based on django-email-usernames by Hakan Waara
# https://bitbucket.org/hakanw/django-email-usernames
class EmailUsernameRegistrationForm(RegistrationFormUniqueEmail):
    """Registration form that uses the user's email address for the username"""

    # If django-passwords is installed, replace the password fields with
    # the fields from this package for extra validation
    try:
        from passwords.fields import PasswordField
        password1 = PasswordField(label=_("Password"))
        password2 = PasswordField(label=_("Password (again)"))
    except ImportError:
        pass

    required_css_class = 'required'

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
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30, required=False)
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'I have agree to the terms of service'),
                             error_messages={'required': _("You must agree to the terms to register")})

    required_css_class = 'required'
