"""Common context processors used across StoryBase apps"""

import json

from django.conf import settings
from django.contrib.sites.models import Site, RequestSite
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from storybase import settings as storybase_settings

def conf(request):
    """Add selected settings values to the template context"""
    context = {}

    for setting in storybase_settings.SETTING_ATTRS:
        setting_val = getattr(settings, setting, None)
        if setting_val is not None:
            if setting in storybase_settings.JSON_SETTINGS:
                # Value needs to be JSONified
                setting_val = mark_safe(json.dumps(setting_val))
            else:
                if isinstance(setting_val, (str, unicode)):
                    # Value is text, translate it
                    setting_val = _(setting_val)

            context.update({setting.lower(): setting_val})


    return context

def site(request):
    """
    Add site info to request context

    From http://djangosnippets.org/snippets/1197/
    """
    site_info = {'protocol': request.is_secure() and 'https' or 'http'}
    if Site._meta.installed:
        site_info['domain'] = Site.objects.get_current().domain
    else:
        site_info['domain'] = RequestSite(request).domain
    return site_info
