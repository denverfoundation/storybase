from itertools import chain
from django.template import Library, Context
from django.template.loader import get_template
from cmsplugin_storybase.models import NewsItem
from storybase_story.models import Story
from storybase_user.models import Project

register = Library()

@register.simple_tag
def featured_items(count=4, img_width=335, objects=None):
    if objects is None:
        stories = Story.objects.on_homepage().order_by('-created')
        news = NewsItem.objects.on_homepage().order_by('-created')
        projects = Project.objects.on_homepage().order_by('-created')
        objects = chain(stories, news, projects)
    normalized = [obj.normalize_for_view(img_width) for obj in objects]
    template = get_template('storybase/featured_object.html')
    context = Context({
        'objects': normalized,
    })
    return template.render(context)
