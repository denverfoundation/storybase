from django.conf import settings

STORYBASE_GEOCODER = getattr(settings, 'STORYBASE_GEOCODER',
                             'geopy.geocoders.OpenMapQuest')
"""
String containing import path of geocoder class.

Class should implement geopy's Geocoder interface.

"""

STORYBASE_GEOCODER_ARGS = getattr(settings, 'STORYBASE_GEOCODER_ARGS', {})
"""
Keyword arguments to be passed to the constructor of the geocoder object.
"""

STORYBASE_GEOCODE_EXACTLY_ONE = getattr(settings,
                                        'STORYBASE_GEOCODE_EXACTLY_ONE', False)
"""
Should the geocoder return more than one result?
"""
