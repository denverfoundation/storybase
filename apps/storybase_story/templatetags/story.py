from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _

from storybase.utils import full_url
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

@register.simple_tag
def connected_story_section(section):
    return section.render(show_title=False)

@register.simple_tag
def featured_stories(count=4, img_width=335):
    qs = Story.objects.on_homepage().order_by('-last_edited')[:count]
    objects = [obj.normalize_for_view(img_width) for obj in qs]
    template = get_template('storybase/featured_object.html')
    context = Context({
        "objects": objects,
        "more_link_text": _("View All Stories"),
        "more_link_url": reverse("explore_stories"),
    })
    return template.render(context)

@register.inclusion_tag('storybase_story/story_embed.html')
def story_embed(story):
    return {
        'default_embed_widget_height': DEFAULT_EMBED_WIDGET_HEIGHT,
        'story': story,
        'storybase_site_name': settings.STORYBASE_SITE_NAME,
        'widget_js_url': full_url(settings.STATIC_URL + 'js/widgets.min.js'),
    }
