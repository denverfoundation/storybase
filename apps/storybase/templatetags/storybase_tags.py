from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

from storybase import settings as storybase_settings
from storybase.utils import full_url

register = template.Library()


@register.filter
@stringfilter
def firstparagraph(value):
    # TODO: Clean this up a bit so it can handle HTML and the length parameter
    from storybase.utils import first_paragraph
    return first_paragraph(value)
# TODO: Figure out why is_safe isn't being honored
firstparagraph.is_safe = True

class StorybaseConfNode(template.Node):
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
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if not (format_string[0] == format_string[-1] and format_string[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return StorybaseConfNode(format_string[1:-1])

@register.simple_tag
def featured_asset(obj, width=500):
    return obj.render_featured_asset(format='html', width=width)


@register.simple_tag
def fullurl(path):
    return full_url(path)
