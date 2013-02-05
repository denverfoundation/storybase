from django import template
from storybase.utils import latest_context
from storybase_user.models import Organization

register = template.Library()

@register.inclusion_tag("storybase/latest_objects.html")
def latest_organizations(count=3, img_width=100):
    return latest_context(Organization.objects.all(), count, img_width)
