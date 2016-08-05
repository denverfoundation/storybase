from django import forms
from django.conf import settings
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.template import Context, loader
from django.utils.translation import ugettext_lazy as _

from storybase.utils import get_site_name

class EmailAuthenticationForm(AuthenticationForm):
    # Update the label and maximum length of the username field
    # to reflect our use of e-mail addresses
    username = forms.CharField(label=_("Email"), max_length=254)

    def __init__(self, request=None, *args, **kwargs):
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
        # Set the template to use for the error message
        self.inactive_error_template = kwargs.get('inactive_error_template',
            "registration/account_inactive_error_message.html")
        self.extra_context = kwargs.get('extra_context', {})

    def get_inactive_error_message(self):
        """Return an error message for when the account is inactive

        Uses a template to generate the message.

        """
        user = self.user_cache
        template = loader.get_template(self.inactive_error_template)
        context = {
            'name': user if user.first_name else user.username,
            'site_name': get_site_name(),
            'site_contact_email': settings.STORYBASE_CONTACT_EMAIL
        }
        context.update(self.extra_context)
        return template.render(Context(context))

    def clean(self):
        """Override the default validation error message

        Reference the email address field instead of username and provides a
        more verbose, templated error message for inactive users.

        """
        try:
            return super(EmailAuthenticationForm, self).clean()
        except forms.ValidationError:
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct email address and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.get_inactive_error_message())


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

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        from storybase_user.auth.utils import send_password_reset_email
        for user in self.get_users(self.cleaned_data['email']):
            send_password_reset_email(user,
                domain_override=domain_override,
                subject_template_name=subject_template_name,
                email_template_name=email_template_name,
                use_https=use_https,
                token_generator=token_generator,
                from_email=from_email,
                request=request,
                extra_context=self.get_custom_context(request))

class ChangeUsernameEmailForm(forms.Form):
    """Form for changing the username/email

    This works under the current scheme where username and email address are
    the same

    """
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput,
            help_text=_("For your security, you must enter your password to change your email address"))
    new_email1 = forms.CharField(label=_("New email address"))
    new_email2 = forms.CharField(label=_("New email address confirmation"))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.previous_data = {}
        super(ChangeUsernameEmailForm, self).__init__(*args, **kwargs)

    def user_exists(self, email):
        q = Q(username=email) | Q(email=email)
        try:
            User.objects.get(q)
            return True
        except User.DoesNotExist:
            return False

    def clean_password(self):
        """
        Validates that the password field is correct.
        """
        password = self.cleaned_data["password"]
        if not self.user.check_password(password):
            raise forms.ValidationError(_("Your password was entered incorrectly. Please enter it again."))
        return password

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(_("The two email fields didn't match."))
            if self.user_exists(new_email2):
                raise forms.ValidationError(_("A user with this email address already exists."))
        return new_email2

    def save(self, commit=True):
        self.previous_data['email'] = self.user.email
        self.user.username = self.user.email = self.cleaned_data['new_email1']
        if commit:
            self.user.save()
        return self.user
