"""Custom pipeline steps for django-social-auth"""

import logging

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect


logger = logging.getLogger('storybase')

def get_data_from_user(request, *args, **kwargs):
    """Get additional account details provided by user"""
    strategy = kwargs.get('strategy')
    details = kwargs.get('details')
    out = {}
    email = strategy.session_get('new_account_email')
    username = strategy.session_get('new_account_username')

    out['username'] = username

    if email:
        details['email'] = email

    # Remove the flag that indicates extra information exists from the
    # session, otherwise, the user will bypass entering the additional
    # account information if their account is deleted and they recreate
    # the account.  See issue #136
    if strategy.session_get('new_account_extra_details'):
        strategy.session_pop('new_account_extra_details')

    return out

def redirect_to_form(*args, **kwargs):
    """Redirect user to form to get additional account information"""
    strategy = kwargs.get('strategy')
    # Save the username to the session so it can be passed to later
    # pipeline steps
    strategy.session_set('new_account_username', kwargs.get('username'))

    if (not strategy.session_get('new_account_extra_details') and
            kwargs.get('user') is None):
        redirect_url = reverse('account_extra_details')
        return HttpResponseRedirect(redirect_url)
    else:
        logger.info('Bypassing collecting additional registration details')
        return None
