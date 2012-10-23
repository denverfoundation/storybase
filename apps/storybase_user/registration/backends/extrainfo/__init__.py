"""Custom registration backend

Collects additional information when registering the user

"""

from django.conf import settings
from django.contrib.auth import login

from registration.backends.default import DefaultBackend
from registration.signals import user_activated

from storybase_user.registration.forms import ExtraInfoRegistrationForm

class ExtraInfoBackend(DefaultBackend):
    """Backend class that collects additional information"""
    def register(self, request, **kwargs):
        new_user = super(ExtraInfoBackend, self).register(request, **kwargs)
        new_user.first_name = kwargs['first_name']
        new_user.last_name = kwargs['last_name']
        new_user.save()
        return new_user

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return ExtraInfoRegistrationForm

    def post_activation_redirect(self, request, user):
        """
        Redirect the user to the home page after successful
        account activation.
        
        """
        return (settings.LOGIN_REDIRECT_URL, (), {})


def login_on_activation(sender, user, request, **kwargs):
    """Log the user in after successful account activation"""
    user.backend = 'storybase_user.auth.backends.EmailModelBackend'
    login(request, user)
user_activated.connect(login_on_activation) 
