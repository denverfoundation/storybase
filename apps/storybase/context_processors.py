"""Common context processors used across StoryBase apps"""

from django.conf import settings
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

def conf(request):
    """Add selected settings values to the template context"""
    setting_attrs = ('ADDTHIS_PUBID', 'GA_PROPERTY_ID', 'GA_DOMAIN_NAME',
		    'STORYBASE_SITE_NAME', 'STORYBASE_SITE_TAGLINE',
		    'STORYBASE_EXPLORE_TITLE', 
		    'STORYBASE_ORGANIZATION_LIST_TITLE',
		    'STORYBASE_PROJECT_LIST_TITLE', 'STORYBASE_MAP_CENTER')
    json_settings = ('STORYBASE_MAP_CENTER',)
    context = {}

    for setting in setting_attrs:
        setting_val = getattr(settings, setting, None)
        if setting_val is not None:
            if setting in json_settings:
                # Value needs to be JSONified
                setting_val = mark_safe(simplejson.dumps(setting_val))
            else:
                # Value is text, translate it
                setting_val = _(setting_val)

            context.update({setting.lower(): setting_val})
    

    return context
