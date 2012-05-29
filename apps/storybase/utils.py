"""Shared utility functions"""

from django.conf import settings
from django.template.defaultfilters import slugify as django_slugify
from django.utils.translation import ugettext as _

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
