from django import template
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
import random # temp

register = template.Library()

@register.simple_tag
def featured_projects(count = 4):
    # temp: should actually pull projects, etc.    
    # currently the template asks for a "normalized" dictionary format, so 
    # note that passing raw project objects won't work.

    #projects = Project.objects.on_homepage().order_by('-last_edited')[:count]
    projects = []
    for i in range(count):
        projects.append({ 
            "title": "Project %d Title" % (i + 1),
            "author": "Author Name", 
            "date": "August 25, 2012", 
            "image_url": "img/image%d.jpg" % random.randrange(1, 9), 
            "excerpt": "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum." 
        })

    template = get_template('storybase/featured_object.html')
    # STATIC_URL should be included via context processor ... not sure best way to do that
    context = Context({ "objects": projects, "more_link_text": "View Projects", "more_link_url": "/projects", "STATIC_URL": settings.STATIC_URL })
    return template.render(context)