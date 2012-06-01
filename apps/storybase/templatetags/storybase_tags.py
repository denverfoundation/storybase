from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def firstparagraph(value):
    # TODO: Clean this up a bit so it can handle HTML and the length parameter
    from storybase.utils import first_paragraph
    return first_paragraph(value)
# TODO: Figure out why is_safe isn't being honored
firstparagraph.is_safe = True
