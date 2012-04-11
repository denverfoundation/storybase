"""Common context processors used across StoryBase apps"""

from django.conf import settings

def conf(request):
    """Add selected settings values to the template context"""
    context = {}
    for setting in ('GA_PROPERTY_ID', 'ADDTHIS_PUBID'):
        setting_val = getattr(settings, setting, None)
        if setting_val is not None:
            context.update({setting.lower(): setting_val})

    return context
