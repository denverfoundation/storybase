"""Custom pipeline steps for django-social-auth"""

import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from social_auth.backends.exceptions import StopPipeline

logger = logging.getLogger('storybase')

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

    # Remove the flag that indicates extra information exists from the
    # session, otherwise, the user will bypass entering the additional
    # account information if their account is deleted and they recreate
    # the account.  See issue #136
    if 'new_account_extra_details' in request.session:
        del request.session['new_account_extra_details']

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
        logger.info('Bypassing collecting additional registration details')
        return None
