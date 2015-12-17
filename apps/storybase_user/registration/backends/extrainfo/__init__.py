"""Custom registration backend

Collects additional information when registering the user

"""

from django.contrib.auth import login

def login_on_activation(sender, user, request, **kwargs):
    """
    Log the user in after successful account activation

    In order to enable this behavior, one needs to connect this
    function to the ``registration.signals.user_activated`` signal.

    """
    user.backend = 'storybase_user.auth.backends.EmailModelBackend'
    login(request, user)
