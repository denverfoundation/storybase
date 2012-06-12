from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class EmailAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
        # Update the label and maximum lenght of the username field
        # to reflect our use of e-mail addresses
        self.fields['username'].max_length = 254
        self.fields['username'].label = _("Email")

    def clean(self):
        """Override the default validation error message
        
        Reference the email address field instead of username

        """
        try:
            return super(EmailAuthenticationForm, self).clean()
        except forms.ValidationError:
            raise forms.ValidationError(_("Please enter a correct email address and password. Note that both fields are case-sensitive."))
