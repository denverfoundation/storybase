"""Custom registration backend

Collects additional information when registering the user

"""
import re

from registration.backends.default import DefaultBackend

from storybase_user.registration.forms import ExtraInfoRegistrationForm

class ExtraInfoBackend(DefaultBackend):
    """Backend class that collects additional information"""
    def _split_name(self, full_name):
        first_name = ""
        last_name = ""
        # Split the name along whitespace
        name_chunks = re.split(r'\s+', full_name)
        if len(name_chunks):
            if len(name_chunks) >= 2:
                first_name = ' '.join(name_chunks[:-1])
                last_name = name_chunks[-1]
            else:
                # Only one part of the name, set the first name
                first_name = name_chunks[0]

        return (first_name, last_name)

    def register(self, request, **kwargs):
        new_user = super(ExtraInfoBackend, self).register(request, **kwargs)
        (first_name, last_name) = self._split_name(kwargs['full_name'])
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()
        return new_user

    def get_form_class(self, request):
        """
        Return the default form class used for user registration.
        
        """
        return ExtraInfoRegistrationForm
