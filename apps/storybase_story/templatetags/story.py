from django import template
from storybase_story.views import (render_featured_projects, render_featured_stories)

register = template.Library()

@register.simple_tag(takes_context=True)
def container(context, name):
    try:
        return context['asset_content'][name]
    except KeyError:
        return '<div class="storybase-container-placeholder" id="%s"></div>' % (name)

@register.simple_tag
def featured_stories(count = 4):
    return render_featured_stories(count);

# should this go in _user?
@register.simple_tag
def featured_projects(count = 4):
    return render_featured_projects(count);