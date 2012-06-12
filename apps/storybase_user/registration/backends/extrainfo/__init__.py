"""Custom registration backend

Collects additional information when registering the user

"""

from registration.backends.default import DefaultBackend

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
