"""Common context processors used across StoryBase apps"""

from django.conf import settings

def conf(request):
    """Add selected settings values to the template context"""
    context = {}
    ga_property_id = getattr(settings, 'GA_PROPERTY_ID', None)
    if ga_property_id is not None:
        context.update({'ga_property_id': ga_property_id})

    return context
