"""Shared utility functions"""

import pytz

from django.conf import settings
from django.template.defaultfilters import slugify as django_slugify
from django.utils.translation import ugettext_lazy as _

def get_language_name(language_code):
    """Convert a language code into its full (localized) name"""
    languages = dict(settings.LANGUAGES)
    return _(languages[language_code])


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    converts spaces to hyphens, and truncates to 50 characters.
    """
    slug = django_slugify(value)
    slug = slug[:50]
    return slug.rstrip('-')


def simple_language_changer(func):
    """
    Proxy for the menus.simple_language_changer decorator

    If the menus app is not installed, the original function is returned.
    This allows view code to be easily decoupled from Django CMS.
    """
    if 'menus' in settings.INSTALLED_APPS:
        from menus.utils import simple_language_changer
        return simple_language_changer(func)
    else:
        return func


# TODO: Test this a bit, make signature match handlebars implementation
def first_paragraph(value): 
    import re
    from lxml.html import fragments_fromstring, tostring
    fragments = fragments_fromstring(value)
    if len(fragments):
        for fragment in fragments:
            if getattr(fragment, 'tag', None) == 'p':
                fragment.drop_tag()
                return tostring(fragment)

    graphs = re.split(r'[\r\n]{2,}', value)
    return graphs[0]


def import_class(import_path):
    """Return a class object from its import path"""
    path_parts = import_path.split('.')
    class_name = path_parts[-1]
    module_name = '.'.join(path_parts[:-1])
    module = __import__(module_name, globals(), locals(), [class_name], -1)
                        
    return getattr(module, class_name)

def add_tzinfo(dt, tzname=settings.TIME_ZONE):
    """
    Return a timezone aware version of a datetime object, taking into
    account daylight savings time

    Arguments:
    dt     -- A timezone naive datetime.datetime object
    tzname -- A timezone name, e.g. 'America/Chicago'. Defaults to 
              settings.TIME_ZONE
    
    """
    tz = pytz.timezone(settings.TIME_ZONE).localize(dt).tzinfo
    return dt.replace(tzinfo=tz)
