from django import template
from django.core.exceptions import ObjectDoesNotExist
from storybase_asset.models import Asset
from django.template.loader import get_template
from django.template import Context
import random # temp

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
    # temp: should actually pull stories, etc.
    # currently the template asks for a "normalized" dictionary format, so 
    # note that passing raw project objects may not work.
    stories = []
    for i in range(count):
        stories.append({ 
            "title": "Story %d Title" % (i + 1),
            "author": "Author Name", 
            "date": "August 25, 2012", 
            "image_url": "/static/css/images/image%d.jpg" % random.randrange(1, 9), 
            "excerpt": "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum." 
        })
    template = get_template('storybase/featured_object.html')
    context = Context({ "objects": stories, "more_link_text": "View Stories", "more_link_url": "/stories"})
    return template.render(context)
