import re
from urllib import urlencode

from django.conf import settings
from django.template import (Node, Library, TemplateSyntaxError, Variable,
                             VariableDoesNotExist)
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_unicode

from storybase import settings as storybase_settings
from storybase.utils import full_url

register = Library()

@register.filter
@stringfilter
def firstparagraph(value):
    # TODO: Clean this up a bit so it can handle HTML and the length parameter
    from storybase.utils import first_paragraph
    return first_paragraph(value)
# TODO: Figure out why is_safe isn't being honored
firstparagraph.is_safe = True


@register.filter
def classname(value):
    """Return the class name of an object"""
    return value.__class__.__name__


camel_re = re.compile('([a-z])([A-Z])')
@register.filter
def camelsplit(value):
    """Split a camel-cased string into a list"""
    return camel_re.sub(r'\1_\2', value).split('_')


class StorybaseConfNode(Node):
    def __init__(self, attr):
        self.attr = attr.upper()

    def render(self, context):
        if self.attr in storybase_settings.SETTING_ATTRS:
            # TODO: Figure out how I want to handle marking text safe and
            # serializing certain variables into JSON
            return getattr(settings, self.attr, None)

        return None

@register.tag
def storybase_conf(parser, token):
    """
    Template tag for accessing Storybase configuration variables

    The preferred method of accessing these configuration values is through
    the ``conf`` context processor, but this template tag is useful for cases
    where the template isn't rendered with a RequestContext object or you
    can't modify the context passed to the template (such as in a third-party
    app)

    """
    try:
        tag_name, format_string = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return StorybaseConfNode(format_string[1:-1])

@register.simple_tag
def featured_asset(obj, width=500):
    return obj.render_featured_asset(format='html', width=width)


@register.simple_tag
def featured_asset_thumbnail_url(obj, include_host=True, width=240, height=240):
    return obj.featured_asset_thumbnail_url(include_host, width, height)


@register.simple_tag
def ga_campaign_params(source, medium, campaign, term=None, content=None,
                       prefix="?"):
    """
    Add custom campaign paramaters to a URL

    See https://support.google.com/analytics/bin/answer.py?hl=en&answer=1033863&topic=1032998&ctx=topic
    """
    # Is Google Analytics enabled?
    ga_enabled = hasattr(settings, 'GA_PROPERTY_ID')
    if not ga_enabled:
        # Google Analytics is not enabled, just return the default URL
        return ""

    params = {
        'utm_source': source,
        'utm_medium': medium,
        'utm_campaign': campaign,
    }

    if term:
        params['utm_term'] = term

    if content:
        params['utm_content'] = content

    return "%s%s" % (prefix, urlencode(params))


class FullURLNode(Node):
    def __init__(self, path, asvar):
        self.path = Variable(path)
        self.asvar = asvar

    def render(self, context):
        from storybase.utils import full_url
        try:
            url = full_url(self.path.resolve(context))
        except VariableDoesNotExist:
            url = ''

        if self.asvar:
            context[self.asvar] = url
            return ''
        else:
            return url

@register.tag
def fullurl(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (a URL path)" % bits[0])
    path = bits[1]
    asvar = None
    bits = bits[2:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]

    return FullURLNode(path, asvar)

# "an" filter by SmileyChris
# http://djangosnippets.org/snippets/1519/
CONSONANT_SOUND = re.compile(r'''
one(![ir])
''', re.IGNORECASE|re.VERBOSE)
VOWEL_SOUND = re.compile(r'''
[aeio]|
u([aeiou]|[^n][^aeiou]|ni[^dmnl]|nil[^l])|
h(ier|onest|onou?r|ors\b|our(!i))|
[fhlmnrsx]\b
''', re.IGNORECASE|re.VERBOSE)

@register.filter
@stringfilter
def an(text):
    """
    Guess "a" vs "an" based on the phonetic value of the text.

    "An" is used for the following words / derivatives with an unsounded "h":
    heir, honest, hono[u]r, hors (d'oeuvre), hour

    "An" is used for single consonant letters which start with a vowel sound.

    "A" is used for appropriate words starting with "one".

    An attempt is made to guess whether "u" makes the same sound as "y" in
    "you".
    """
    text = force_unicode(text)
    if not CONSONANT_SOUND.match(text) and VOWEL_SOUND.match(text):
        return 'an'
    return 'a'


# Height in pixels of the IFRAME element rendered by the story
# embed widget
DEFAULT_EMBED_WIDGET_HEIGHT=500

def _object_name(obj):
    """
    Get the name if a model instance

    Returns the ``title`` attribute if it's present, if not,
    returns the ``name`` attribute. If neither is present,
    return an empty string.

    """
    try:
        return getattr(obj, 'title')
    except AttributeError:
        return getattr(obj, 'name', '')

@register.inclusion_tag('storybase/embed_code.html')
def embed_code(obj):
    return {
        'default_embed_widget_height': DEFAULT_EMBED_WIDGET_HEIGHT,
        'object': obj,
        'embed_class': ('storybase-story-embed' if obj.__class__.__name__ == 'Story'
                        else 'storybase-list-embed'),
        'object_name': _object_name(obj),
        'storybase_site_name': settings.STORYBASE_SITE_NAME,
        'widget_js_url': full_url(settings.STATIC_URL + 'js/widgets.min.js',
                                  scheme=''),
    }
