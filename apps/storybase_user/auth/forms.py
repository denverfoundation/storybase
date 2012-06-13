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
        from django.core.mail import send_mail
        from django.contrib.sites.models import get_current_site
        from django.template import Context, loader
        from django.utils.http import int_to_base36
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            # Update the context dict with custom context
            # At first, I thought I could just use RequestContext, but this
            # clobbers the user variable
            c.update(self.get_custom_context(request))
            send_mail(_("Password reset on %s") % site_name,
                t.render(Context(c)), from_email, [user.email])
