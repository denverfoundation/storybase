from itertools import chain
from django.contrib.auth.models import AnonymousUser
from django.template import Library, Context
from django.template.loader import get_template
from cmsplugin_storybase.models import NewsItem
from storybase_story.models import Story
from storybase_user.models import Project

register = Library()

@register.simple_tag(takes_context=True)
def featured_items(context, count=4, img_width=335, objects=None):
    if objects is None:
        stories = Story.objects.on_homepage().order_by('-created')
        news = NewsItem.objects.on_homepage().order_by('-created')
        projects = Project.objects.on_homepage().order_by('-created')
        objects = chain(stories, news, projects)
    if 'user' in context:
        user = context['user']
    else:
        user = AnonymousUser()
    normalized = [obj.normalize_for_view(img_width) for obj in objects
                  if obj.has_perm(user, 'view')]
    template = get_template('storybase/featured_object.html')
    context = Context({
        'objects': normalized,
    })
    return template.render(context)
