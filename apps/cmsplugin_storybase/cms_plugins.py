from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from models import StoryPlugin as StoryPluginModel
from django.utils.translation import ugettext as _

class StoryPlugin(CMSPluginBase):
    model = StoryPluginModel
    name = _("StoryBase Story")
    render_template = "story_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context

plugin_pool.register_plugin(StoryPlugin)
