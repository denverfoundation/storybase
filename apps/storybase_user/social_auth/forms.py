"""Custom forms for authentication and registration"""
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

# TODO: See if this can be merged with 
# storybase_user.registration.forms.ExtraInfoRegistrationForm
class TosForm(forms.Form):
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
        label=_(u'I agree to the terms of service'),
        error_messages={
            'required': _("You must agree to the terms to register")
        })

class EmailTosForm(TosForm):
    email = forms.EmailField()

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the site.
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. You must first log in to your account with your password and then associate your social media account."))
        return self.cleaned_data['email']

