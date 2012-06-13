from django import forms
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth.tokens import default_token_generator
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


class StrongSetPasswordForm(SetPasswordForm):
    """A version of SetPasswordForm that uses fields from django-passwords if available"""
    # If django-passwords is installed, replace the password fields with
    # the fields from this package for extra validation
    try:
        from passwords.fields import PasswordField
        new_password1 = PasswordField(label=_("New password"))
        new_password2 = PasswordField(label=_("New password confirmation"))
    except ImportError:
        pass


# HACK: This seems like an inelegant way to pass additional context to the
# e-mail template
class CustomContextPasswordResetForm(PasswordResetForm):
    def get_custom_context(self, request):
        """Return a dictionary of context variables

        These are added to the template context for the email template

        """
        from storybase.context_processors import conf
        # Return site-wide configuration context variables 
        context = conf(request)
        return context 

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from storybase_user.auth.utils import send_password_reset_email
        for user in self.users_cache:
            send_password_reset_email(user,
                domain_override=domain_override, 
                email_template_name=email_template_name,
                use_https=use_https,
                token_generator=token_generator,
                from_email=from_email,
                request=request,
                extra_context=self.get_custom_context(request))
