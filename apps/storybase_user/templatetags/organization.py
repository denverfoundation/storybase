from django import template
from django.conf import settings
from storybase.utils import full_url, latest_context
from storybase_user.models import Organization

register = template.Library()

# Height in pixels of the IFRAME element rendered by the story
# embed widget
# TODO: @see story template tags, refactor wrt story embed
DEFAULT_EMBED_WIDGET_HEIGHT=500

@register.inclusion_tag("storybase/latest_objects.html")
def latest_organizations(count=3, img_width=100):
    return latest_context(Organization.objects.all(), count, img_width)

@register.inclusion_tag('storybase_user/object_embed.html')
def organization_embed(organization):
    return {
        'default_embed_widget_height': DEFAULT_EMBED_WIDGET_HEIGHT,
        'object': organization,
        'storybase_site_name': settings.STORYBASE_SITE_NAME,
        'widget_js_url': full_url(settings.STATIC_URL + 'js/widgets.min.js')
    }
