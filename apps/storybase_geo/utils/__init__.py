from storybase.utils import import_class

def get_geocoder():
    """Get a geocoder object based on the settings"""
    from storybase_geo import settings
    geocoder_class = import_class(settings.STORYBASE_GEOCODER)
    return geocoder_class(**settings.STORYBASE_GEOCODER_ARGS)
