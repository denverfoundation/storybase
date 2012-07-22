from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def container(context, name):
    try:
        return context['asset_content'][name]
    except KeyError:
        return '<div class="storybase-container-placeholder" id="%s"></div>' % (name)
