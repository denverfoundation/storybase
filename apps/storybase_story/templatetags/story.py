from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from storybase.utils import full_url, latest_context
from storybase_asset.models import Asset
from storybase_story.models import Story

register = template.Library()

# Height in pixels of the IFRAME element rendered by the story
# embed widget
DEFAULT_EMBED_WIDGET_HEIGHT=500

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

@register.inclusion_tag("storybase_story/connected_story.html")
def connected_story(story):
    return {
        'story': story,
    }

@register.inclusion_tag("storybase/latest_objects.html")
def latest_stories(count=3, img_width=100):
    return latest_context(Story, count, img_width)

@register.simple_tag
def connected_story_section(section):
    return section.render(show_title=False)

@register.inclusion_tag('storybase_story/story_embed.html')
def story_embed(story):
    return {
        'default_embed_widget_height': DEFAULT_EMBED_WIDGET_HEIGHT,
        'story': story,
        'storybase_site_name': settings.STORYBASE_SITE_NAME,
        'widget_js_url': full_url(settings.STATIC_URL + 'js/widgets.min.js'),
    }
