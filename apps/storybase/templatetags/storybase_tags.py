import re

from django.conf import settings
from django.template import (Node, Library, TemplateSyntaxError, Variable,
                             VariableDoesNotExist)
from django.template.defaultfilters import stringfilter

from storybase import settings as storybase_settings

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
