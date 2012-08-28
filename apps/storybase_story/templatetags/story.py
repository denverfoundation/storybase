from django import template
from django.core.exceptions import ObjectDoesNotExist

from storybase_asset.models import Asset
from storybase_story.views import (render_featured_projects, render_featured_stories)

register = template.Library()

@register.simple_tag(takes_context=True)
def container(context, value):
    if hasattr(value, 'weight'):
        # Argument is a SectionAsset model instance
        asset = value.asset
    else:
        # Argument is a string
        try:
            asset = context['assets'].get(container__name=value).asset
        except (KeyError, ObjectDoesNotExist):
            # Either the context doesn't have an "assets" attribute or there
            # is no asset matching the container
            return '<div class="storybase-container-placeholder" id="%s"></div>' % (value)

    # Get the asset subclass instance
    asset = Asset.objects.get_subclass(pk=asset.pk)
    return asset.render_html()

@register.simple_tag
def featured_stories(count = 4):
    return render_featured_stories(count);

# should this go in _user?
@register.simple_tag
def featured_projects(count = 4):
    return render_featured_projects(count);
