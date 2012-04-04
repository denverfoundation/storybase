from django.utils.translation import ugettext as _

from cms.models.pluginmodel import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from storybase_story.views import homepage_story_list

from models import StoryPlugin as StoryPluginModel

class StoryPlugin(CMSPluginBase):
    model = StoryPluginModel
    name = _("StoryBase Story")
    render_template = "story_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context

class HomepageStoriesPlugin(CMSPluginBase):
    model = CMSPlugin
    name = _("StoryBase Homepage Stories")
    render_template = "homepage_stories_plugin.html"

    def render(self, context, instance, placeholder):
        context['story_list'] = homepage_story_list() 
	return context 

plugin_pool.register_plugin(StoryPlugin)
plugin_pool.register_plugin(HomepageStoriesPlugin)
