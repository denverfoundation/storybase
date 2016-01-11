from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool

from storybase_messaging.forms import SiteContactMessageForm
from storybase_story.forms import StorySearchForm
from storybase_badge.models import Badge

from cmsplugin_storybase.models import (ActivityPlugin as ActivityPluginModel,
    StoryPlugin as StoryPluginModel,
    HelpPlugin as HelpPluginModel)


class ActivityPlugin(CMSPluginBase):
    model = ActivityPluginModel
    name = _("StoryBase Activity")
    render_template = "cmsplugin_storybase/activity_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context

class ContactFormPlugin(CMSPluginBase):
    model = CMSPlugin
    name = _("StoryBase Contact Form")
    render_template = "sitecontactmessage_form_plugin.html"

    def render(self, context, instance, placeholder):
        context['form'] = SiteContactMessageForm()
        return context


class StoryPlugin(CMSPluginBase):
    model = StoryPluginModel
    name = _("StoryBase Story")
    render_template = "story_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context


class HelpPlugin(CMSPluginBase):
    model = HelpPluginModel
    name = _("StoryBase Help")
    render_template = "cmsplugin_storybase/help_plugin.html"

    def render(self, context, instance, placeholder):
        context['instance'] = instance
        return context


class BadgesPlugin(CMSPluginBase):
    model = CMSPlugin
    name = _("StoryBase Badges")
    render_template = "badges_plugin.html"

    def render(self, context, instance, placeholder):
        context['badges'] = Badge.objects.all()
        return context


class SearchPlugin(CMSPluginBase):
    model = CMSPlugin
    name = _("StoryBase Search")
    render_template = "search_plugin.html"

    def render(self, context, instance, placeholder):
         context['form'] = StorySearchForm
         return context


plugin_pool.register_plugin(ActivityPlugin)
plugin_pool.register_plugin(ContactFormPlugin)
plugin_pool.register_plugin(StoryPlugin)
plugin_pool.register_plugin(HelpPlugin)
plugin_pool.register_plugin(BadgesPlugin)
plugin_pool.register_plugin(SearchPlugin)
