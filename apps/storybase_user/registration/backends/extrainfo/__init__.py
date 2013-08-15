"""Custom registration backend

Collects additional information when registering the user

"""

from django.conf import settings
from django.contrib.auth import login

from registration.signals import user_activated

def login_on_activation(sender, user, request, **kwargs):
    """Log the user in after successful account activation"""
    user.backend = 'storybase_user.auth.backends.EmailModelBackend'
    login(request, user)
user_activated.connect(login_on_activation) 
