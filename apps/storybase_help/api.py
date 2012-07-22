from django.conf.urls.defaults import url

from tastypie import fields
from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.utils import trailing_slash

from storybase.api import TranslatedModelResource
from storybase_help.models import Help

class HelpResource(TranslatedModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    body = fields.CharField(attribute='body')

    class Meta:
        queryset = Help.objects.all()
        resource_name = 'help'
        allowed_methods = ['get']
        authentication = Authentication()
        authorization = Authorization()
        # Hide the underlying id
        excludes = ['id']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<help_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]
