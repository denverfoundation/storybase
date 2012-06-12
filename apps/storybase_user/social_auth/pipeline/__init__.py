"""Custom pipeline steps for django-social-auth"""

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from social_auth.backends.exceptions import StopPipeline

def get_data_from_user(request, *args, **kwargs):
    """Get additional account details provided by user"""
    details = kwargs.get('details')
    out = {}
    email = request.session.get('new_account_email', None)
    username = request.session.get('new_account_username', None)

    if username:
        out['username'] = username
    else:
        # Should never get here as the username unless the pipeline is
        # not correctly configured and a pipeline step that saves the 
        # username (as returned by get_username()) is not placed before
        # this step
        raise StopPipeline()

    if email:
        details['email'] = email

    return out 

def redirect_to_form(*args, **kwargs):
    """Redirect user to form to get additional account information"""
    request = kwargs.get('request')
    # Save the username to the session so it can be passed to later
    # pipeline steps
    request.session['new_account_username'] = kwargs.get('username')

    if (not request.session.get('new_account_extra_details') and
            kwargs.get('user') is None):
        redirect_url = reverse('account_extra_details')
        return HttpResponseRedirect(redirect_url)
    else:
        return None
