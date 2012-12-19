"""Shared utility functions"""

from urlparse import urlsplit, urlunsplit
import re

import pytz

from django.conf import settings
from django.contrib.sites.models import get_current_site
from django.template.defaultfilters import slugify as django_slugify
from django.utils.translation import ugettext_lazy as _

def get_language_name(language_code):
    """Convert a language code into its full (localized) name"""
    languages = dict(settings.LANGUAGES)
    return _(languages[language_code])


def open_html_element(el, attrs={}):
    chunks = []
    chunks.append("<")
    chunks.append(el)
    for attr, value in attrs.iteritems():
        chunks.append(' %s="%s"' % (attr, value))
    chunks.append(">")
    return "".join(chunks)

def close_html_element(el):
    return "</" + el + ">"


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    converts spaces to hyphens, and truncates to 50 characters.
    """
    slug = django_slugify(value)
    slug = slug[:50]
    return slug.rstrip('-')


# Automate unique slugs by Chris Beaven
# http://djangosnippets.org/snippets/512/
def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len-len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value


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


def get_site_name(request=None):
    """
    Get the site name
    
    Try the setting first, if not try the sites framework.
    
    """
    site_name = getattr(settings, 'STORYBASE_SITE_NAME', None)
    if not site_name:
        current_site = get_current_site(request)
        site_name = current_site.name
    return site_name


def full_url(urlstring, scheme='http'):
    parsed = urlsplit(urlstring)
    if parsed.netloc:
        # URL string is already full, e.g. 
        # http://localhost:8000/stories/foo/, just return it
        return urlstring
    else:
        # URL string does not contain domain/protocol information.
        # It's just a path, e.g. /stories/foo/
        current_site = get_current_site(None)
        return urlunsplit((scheme, current_site.domain, urlstring, None, None))


def key_from_instance(instance, extra=None):
    """
    Generate a cache key for a Django model instance
    """
    opts = instance._meta
    key = '%s.%s:%s' % (opts.app_label, opts.module_name, instance.pk)
    return key if extra is None else key + ":" + extra
