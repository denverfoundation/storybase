from django import template
from storybase.utils import latest_context
from storybase_user.models import Project

register = template.Library()

@register.inclusion_tag("storybase/latest_objects.html")
def latest_projects(count=3, img_width=100):
    return latest_context(Project.objects.all(), count, img_width)
