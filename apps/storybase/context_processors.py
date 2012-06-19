"""Common context processors used across StoryBase apps"""

from django.conf import settings
from django.utils import simplejson
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
                setting_val = mark_safe(simplejson.dumps(setting_val))
            else:
                if isinstance(setting_val, (str, unicode)):
                    # Value is text, translate it
                    setting_val = _(setting_val)

            context.update({setting.lower(): setting_val})
    

    return context
