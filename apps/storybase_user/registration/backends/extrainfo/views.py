import logging

from django.contrib import messages
from django.utils.translation import ugettext as _

from registration.backends.default.views import ActivationView, RegistrationView

from storybase_user.registration.forms import ExtraInfoRegistrationForm

logger = logging.getLogger('storybase')

class ExtraInfoRegistrationView(RegistrationView):
    """Registration view that collects additional information"""
    form_class = ExtraInfoRegistrationForm

    def register(self, form):
        data = form.cleaned_data
        new_user = super(ExtraInfoRegistrationView, self).register(form)
        new_user.username = data['username']
        new_user.first_name = data['first_name']
        new_user.last_name = data['last_name']
        new_user.save()
        return new_user

class ExtraInfoActivationView(ActivationView):
    def handle_activation_failure(self, activation_key):
        logger.warn("Activation with key \"%s\" failed" % activation_key)

    def activate(self, *args, **kwargs):
        activated_user = super(ExtraInfoActivationView, self).activate(*args, **kwargs)
        import pdb
        pdb.set_trace()

        if activated_user:
            messages.success(
                self.request,
                _("Your account activation succeeded. Please log in below.")
            )
        else:
            self.handle_activation_failure(activation_key)

        return activated_user

    def get_success_url(self, user):
        return ('auth_login', (), {})
