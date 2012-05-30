from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from storybase_story.views import homepage_story_list
from storybase_user.views import (homepage_organization_list,
                                  homepage_project_list)

from cmsplugin_storybase.models import List, StoryPlugin as StoryPluginModel

class StoryPlugin(CMSPluginBase):
    model = StoryPluginModel
    name = _("StoryBase Story")
    render_template = "story_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context

class HomepageProjectsPlugin(CMSPluginBase):
    model = List
    name = _("StoryBase Homepage Projects")
    render_template = "homepage_projects_plugin.html"

    def render(self, context, instance, placeholder):
        context['list'] = homepage_project_list(instance.num_items)
	return context 

class HomepageOrganizationsPlugin(CMSPluginBase):
    model = List
    name = _("StoryBase Homepage Organizations")
    render_template = "homepage_organizations_plugin.html"

    def render(self, context, instance, placeholder):
        context['list'] = homepage_organization_list(instance.num_items)
	return context 

class HomepageStoriesPlugin(CMSPluginBase):
    model = List 
    name = _("StoryBase Homepage Stories")
    render_template = "homepage_stories_plugin.html"

    def render(self, context, instance, placeholder):
        context['story_list'] = homepage_story_list(instance.num_items)
	return context 


plugin_pool.register_plugin(StoryPlugin)
plugin_pool.register_plugin(HomepageStoriesPlugin)
plugin_pool.register_plugin(HomepageProjectsPlugin)
plugin_pool.register_plugin(HomepageOrganizationsPlugin)
