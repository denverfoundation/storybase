from django import template
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.template import Context
from django.utils.translation import ugettext as _

from storybase_user.models import Project

register = template.Library()

# TODO: Actually wire in featured image for project
def _mock_image_html(width):
    from django.conf import settings
    import random
    image_url = "%scss/images/image%d.jpg" % (settings.STATIC_URL,
                                              random.randrange(1, 9))
    return "<img src=\"%s\" />" % (image_url)

@register.simple_tag
def featured_projects(count=4, img_width=335):
    # Put project attributes into a "normalized" dictionary format
    qs =  Project.objects.on_homepage().order_by('-last_edited')[:count]
    objects = [obj.normalize_for_view(img_width) for obj in qs]
    template = get_template('storybase/featured_object.html')
    context = Context({
        "objects": objects,
        "more_link_text": _("View All Projects"),
        "more_link_url": reverse("project_list"),
    })
    return template.render(context)
