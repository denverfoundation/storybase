from django.conf.urls.defaults import url

from tastypie import fields
from tastypie import http
from tastypie.authentication import Authentication
from tastypie.exceptions import ImmediateHttpResponse, Unauthorized
from tastypie.utils import trailing_slash
from tastypie.validation import Validation

from storybase.api import TranslatedModelResource, LoggedInAuthorization
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

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        filters = {}
        section_id = kwargs.get('section_id')
        if section_id:
            filters['section__section_id'] = section_id

        new_obj_list = obj_list.filter(**filters)

        return new_obj_list
    
    def assign_help_to_section(self, bundle, **kwargs):
        self.is_valid(bundle)
        # We can assume that there will be a section id because of 
        # this resource's implementation of is_authorized
        section_id = kwargs.get('section_id', None)
        section = Section.objects.get(section_id=section_id)
        bundle.obj = self.obj_get(bundle, help_id=bundle.data['help_id'])
        section.help = bundle.obj
        section.save()
        return bundle

    def authorized_create_detail(self, object_list, bundle, **kwargs):
        """
        Handles checking of permissions to see if the user has authorization
        to POST this resource.
        """
        try: 
            auth_result = self._meta.authorization.create_detail(object_list, bundle)
            section_id = kwargs.get('section_id', None)

            if section_id is None:
                auth_result = False 
            else:
                # Lookup the section. It's owner should match the request's
                section = Section.objects.get(section_id=section_id)
                if not section.story.author == bundle.request.user:
                    auth_result = False 

            if auth_result is not True:
                raise Unauthorized("You are not allowed to access that resource.")

        except Unauthorized, e:
            self.unauthorized_result(e)

        return auth_result

    def obj_create(self, bundle, **kwargs):
        """
        Instead of actually creating an object, delegate to another
        hook
        """
        self.authorized_create_detail(self.get_object_list(bundle.request), 
                bundle, **kwargs)
        return self.assign_help_to_section(bundle, **kwargs)
