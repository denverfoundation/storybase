"""Custom registration backend

Collects additional information when registering the user

"""

from registration.backends.default import DefaultBackend

from storybase_user.registration.forms import ExtraInfoRegistrationForm
from storybase_user.utils import split_name

class ExtraInfoBackend(DefaultBackend):
    """Backend class that collects additional information"""
    def register(self, request, **kwargs):
        new_user = super(ExtraInfoBackend, self).register(request, **kwargs)
        (first_name, last_name) = split_name(kwargs['full_name'])
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        return new_user

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return ExtraInfoRegistrationForm
