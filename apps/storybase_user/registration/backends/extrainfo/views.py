from django.conf import settings

from registration.backends.default.views import ActivationView, RegistrationView

from storybase_user.registration.forms import ExtraInfoRegistrationForm

class ExtraInfoRegistrationView(RegistrationView):
    """Registration view that collects additional information"""
    form_class = ExtraInfoRegistrationForm

    def register(self, request, **cleaned_data):
        new_user = super(ExtraInfoRegistrationView, self).register(request, **cleaned_data)
        new_user.first_name = cleaned_data['first_name']
        new_user.last_name = cleaned_data['last_name']
        new_user.save()
        return new_user

class ExtraInfoActivationView(ActivationView):
    def get_success_url(self, request, user):
        return (settings.LOGIN_REDIRECT_URL, (), {})

