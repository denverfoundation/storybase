from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool

from storybase_messaging.forms import SiteContactMessageForm 

from cmsplugin_storybase.models import StoryPlugin as StoryPluginModel


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


plugin_pool.register_plugin(ContactFormPlugin)
plugin_pool.register_plugin(StoryPlugin)
