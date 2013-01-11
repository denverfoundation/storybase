from django import template
from django.template import Context
from django.template.loader import get_template
from cmsplugin_storybase.models import NewsItem

register = template.Library()

@register.simple_tag
def featured_news(count=4):
    # Put story attributes into a "normalized" dictionary format 
    qs = NewsItem.objects.on_homepage().filter(status='published').order_by('-last_edited')[:count]
    template = get_template('cmsplugin_storybase/featured_news.html')
    context = Context({
        "objects": qs,
    })
    return template.render(context)
