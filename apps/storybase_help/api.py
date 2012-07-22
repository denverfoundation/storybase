from django.conf.urls.defaults import url

from tastypie import fields
from tastypie import http
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from tastypie.validation import Validation

from storybase.api import (DelayedAuthorizationResource,
    TranslatedModelResource, LoggedInAuthorization)
from storybase_story.models import Section
from storybase_help.models import Help

class HelpValidation(Validation):
    def is_valid(self, bundle, request=None):
        errors = {} 
        if bundle.data.get('help_id', None) is None:
            errors['__all__'] = 'You must specify a help_id value'
        return errors

class HelpResource(TranslatedModelResource):
    # Explicitly declare fields that are on the translation model
    title = fields.CharField(attribute='title')
    body = fields.CharField(attribute='body')

    class Meta:
        queryset = Help.objects.all()
        resource_name = 'help'
        list_allowed_methods = ['get', 'post']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        # Hide the underlying id
        excludes = ['id']
        validation = HelpValidation()

        delayed_authorization_methods = []

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
            url(r"^(?P<resource_name>%s)/sections/(?P<section_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]

    def apply_request_kwargs(self, obj_list, request=None, **kwargs):
        filters = {}
        section_id = kwargs.get('section_id')
        if section_id:
            filters['section__section_id'] = section_id

        new_obj_list = obj_list.filter(**filters)

        return new_obj_list

    def is_authorized(self, request, object=None, **kwargs):
        super(HelpResource, self).is_authorized(request, object, **kwargs)

        # The call upstream didn't return an error, let's check some
        # more resource-specific things
        auth_result = True 
        if request.method == 'POST':
            section_id = kwargs.get('section_id', None)
            if section_id:
                # Lookup the section. It's owner should match the request's
                section = Section.objects.get(section_id=section_id)
                if not section.story.author == request.user:
                    auth_result = False 
            else:
                # We only allow posting when a section_id is provided
                auth_result = False
                    
        if not auth_result is True:
            raise ImmediateHttpResponse(response=http.HttpUnauthorized())

    def assign_help_to_section(self, bundle, request=None, **kwargs):
        self.is_valid(bundle, request)
        # We can assume that there will be a section id because of 
        # this resource's implementation of is_authorized
        section_id = kwargs.get('section_id', None)
        section = Section.objects.get(section_id=section_id)
        bundle.obj = self.obj_get(request, help_id=bundle.data['help_id'])
        section.help = bundle.obj
        section.save()
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """
        Instead of actually creating an object, delegate to another
        hook
        """
        return self.assign_help_to_section(bundle, request, **kwargs)
