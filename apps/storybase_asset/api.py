from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist

from tastypie import fields, http
from tastypie.authentication import Authentication
from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from tastypie.validation import Validation

from filer.models import File, Image

from storybase.api import (DataUriResourceMixin,
   DelayedAuthorizationResource, TranslatedModelResource,
   LoggedInAuthorization)
from storybase_asset.models import (Asset, ExternalAsset, HtmlAsset, 
    LocalImageAsset, DataSet, ExternalDataSet, LocalDataSet)
from storybase_story.models import Story

class AssetResource(DataUriResourceMixin, DelayedAuthorizationResource, 
                    TranslatedModelResource):
    # Explicitly declare fields that are on the translation model, or the
    # subclass
    title = fields.CharField(attribute='title', blank=True, default='')
    caption = fields.CharField(attribute='caption', blank=True, default='')
    body = fields.CharField(attribute='body', null=True)
    url = fields.CharField(attribute='url', null=True)
    image = fields.FileField(attribute='image', null=True)
    content = fields.CharField(readonly=True)
    # A "write-only" field for specifying the filename when uploading images
    # This is removed from responses to GET requests
    filename = fields.CharField(null=True)

    class Meta:
        always_return_data = True
        queryset = Asset.objects.select_subclasses()
        resource_name = 'assets'
        allowed_methods = ['get', 'post', 'put']
        authentication = Authentication()
        authorization = LoggedInAuthorization()

        delayed_authorization_methods = ['put_detail']

    def get_object_class(self, bundle=None, request=None, **kwargs):
        if bundle.data.get('image', None):
            return LocalImageAsset
        elif bundle.data.get('body', None): 
            return HtmlAsset
        elif bundle.data.get('url', None):
            return ExternalAsset
        else:
            raise AttributeError

    def get_object_list(self, request):
        """
        Get a list of assets, filtering based on the request's user and 
        the publication status
        
        """
        from django.db.models import Q
        # Only show published stories  
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(owner=request.user)

        return super(AssetResource, self).get_object_list(request).filter(q)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<asset_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})/sections/none%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                kwargs={'no_section': True},
                name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/sections/(?P<section_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
        ]

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a ``Bundle`` or an object (typically a ``Model`` instance),
        it returns the extra kwargs needed to generate a detail URI.

        This version returns the asset_id field instead of the pk
        """
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.obj.asset_id
        else:
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.asset_id

        return kwargs

    def hydrate_image(self, bundle):
        return self._hydrate_file(bundle, Image, 'image', 'filename')

    def build_bundle(self, obj=None, data=None, request=None):
        if obj and obj.__class__ == Asset:
            # We don't have a subclass instance.  This is likely because
            # the object was retrieved through a RelatedField on another
            # resource
            obj = self._meta.queryset.get(asset_id=obj.asset_id)

        return super(AssetResource, self).build_bundle(obj, data, request)

    def obj_create(self, bundle, request=None, **kwargs):
        # Set the asset's owner to the request's user
        if request.user:
            kwargs['owner'] = request.user
        return super(AssetResource, self).obj_create(bundle, request, **kwargs)

    def apply_request_kwargs(self, obj_list, request=None, **kwargs):
        filters = {}
        story_id = kwargs.get('story_id')
        section_id = kwargs.get('section_id')
        no_section = kwargs.get('no_section')
        if story_id:
            filters['stories__story_id'] = story_id
        if section_id:
            filters['sectionasset__section__section_id'] = section_id

        new_obj_list = obj_list.filter(**filters)

        if no_section and story_id:
            new_obj_list = new_obj_list.exclude(sectionasset__section__story__story_id=story_id)

        return new_obj_list

    def dehydrate(self, bundle):
        # Exclude the filename field from the output
        del bundle.data['filename']
        return bundle
    
    def dehydrate_content(self, bundle):
        return bundle.obj.render(format="html")

class DataSetValidation(Validation):
    def is_valid(self, bundle, request=None, **kwargs):
        errors = {} 
        if bundle.data.get('url') and bundle.data.get('file'):
            errors['__all__'] = "You may specify either a URL or a file for the dataset, but not both"

        return errors

class DataSetResource(DataUriResourceMixin,DelayedAuthorizationResource, 
                      TranslatedModelResource):
    # Explicitly declare fields that are on the translation model, or the
    # subclass
    title = fields.CharField(attribute='title')
    description = fields.CharField(attribute='description', blank=True,
                                   default='')
    url = fields.CharField(attribute='url', null=True)
    file = fields.FileField(attribute='file', null=True)
    # A "write-only" field for specifying the filename when uploading images
    # This is removed from responses to GET requests
    filename = fields.CharField(null=True)

    class Meta:
        always_return_data = True
        queryset = DataSet.objects.select_subclasses()
        resource_name = 'datasets'
        list_allowed_methods = ['get', 'post']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        validation = DataSetValidation()
        detail_uri_name = 'dataset_id'

        delayed_authorization_methods = []

    def get_object_class(self, bundle=None, request=None, **kwargs):
        if bundle.data.get('file', None):
            return LocalDataSet
        elif bundle.data.get('url', None):
            return ExternalDataSet
        else:
            raise AttributeError

    def apply_request_kwargs(self, obj_list, request=None, **kwargs):
        filters = {}
        story_id = kwargs.get('story_id')
        if story_id:
            filters['stories__story_id'] = story_id

        new_obj_list = obj_list.filter(**filters)

        return new_obj_list

    def get_object_list(self, request):
        """
        Get a list of assets, filtering based on the request's user and 
        the publication status
        
        """
        from django.db.models import Q
        # Only show published stories  
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(owner=request.user)

        return super(DataSetResource, self).get_object_list(request).filter(q)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
        ]

    def obj_create(self, bundle, request=None, **kwargs):
        story_id = kwargs.get('story_id')
        if story_id:
            try:
                story = Story.objects.get(story_id=story_id) 
                if not story.has_perm(request.user, 'change'):
                    raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the story matching the provided story ID"))
            except ObjectDoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpNotFound("A story matching the provided story ID could not be found"))

        # Set the asset's owner to the request's user
        if request.user:
            kwargs['owner'] = request.user

        # Let the superclass create the object
        bundle = super(DataSetResource, self).obj_create(
            bundle, request, **kwargs)

        if story_id:
            # Associate the newly created dataset with the story
            story.datasets.add(bundle.obj)
            story.save()

        return bundle


    def hydrate_file(self, bundle):
        return self._hydrate_file(bundle, File, 'file', 'filename')

    def dehydrate(self, bundle):
        # Exclude the filename field from the output
        del bundle.data['filename']
        return bundle
