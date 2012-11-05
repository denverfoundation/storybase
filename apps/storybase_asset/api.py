from django import http as django_http
from django.db.models import Q
from django.http import Http404
from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.utils.translation import ugettext as _

from tastypie import fields, http
from tastypie.authentication import Authentication
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, ImmediateHttpResponse
from tastypie.utils import trailing_slash
from tastypie.validation import Validation

from filer.models import File, Image

from storybase.api import (DataUriResourceMixin,
   DelayedAuthorizationResource, TranslatedModelResource,
   LoggedInAuthorization)
from storybase_asset.models import (Asset, ExternalAsset, HtmlAsset, 
    LocalImageAsset, LocalImageAssetTranslation,
    DataSet, ExternalDataSet, LocalDataSet)
from storybase_story.models import Story

class AssetResource(DataUriResourceMixin, DelayedAuthorizationResource, 
                    TranslatedModelResource):
    # Explicitly declare fields that are on the translation model, or the
    # subclass
    title = fields.CharField(attribute='title', blank=True, default='')
    caption = fields.CharField(attribute='caption', blank=True, default='')
    body = fields.CharField(attribute='body', null=True)
    url = fields.CharField(attribute='url', null=True)
    image = fields.FileField(attribute='image', blank=True, null=True)
    content = fields.CharField(readonly=True)
    thumbnail_url = fields.CharField(readonly=True)
    display_title = fields.CharField(attribute='display_title', readonly=True)
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
        # Hide the underlying id
        excludes = ['id']

        featured_list_allowed_methods = ['get', 'put']
        featured_detail_allowed_methods = []
        delayed_authorization_methods = ['put_detail', 'put_featured_list']

    def get_object_class(self, bundle=None, request=None, **kwargs):
        content_fields = ('body', 'image', 'url')
        num_content_fields = 0
        delayed_upload_types = ('image', 'map', 'chart') 
        for name in content_fields:
            if bundle.data.get(name):
                num_content_fields = num_content_fields + 1
        if num_content_fields > 1:
            raise BadRequest("You must specify only one of the following fields: image, body, or url")
        if bundle.data.get('body'):
            return HtmlAsset
        elif bundle.data.get('url'):
            return ExternalAsset
        elif (bundle.data.get('image') or 
              bundle.data.get('type') in delayed_upload_types):
            return LocalImageAsset
        else:
            raise BadRequest("You must specify an image, body, or url") 


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<asset_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
            url(r"^(?P<resource_name>%s)/(?P<asset_id>[0-9a-f]{32,32})/upload%s$" %
                (self._meta.resource_name, trailing_slash()),
                AssetImageUploadView.as_view(), 
                name="api_dispatch_upload"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_list'),
                name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})/featured%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('dispatch_featured_list'),
                kwargs={'featured': True},
                name="api_dispatch_featured_list"),
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

    def dispatch_featured_list(self, request, **kwargs):
        # This is defined as a separate method
        # so dispatch will check which method is allowed separately
        # from the other method handlers
        return self.dispatch('featured_list', request, **kwargs)

    def get_featured_list(self, request, **kwargs):
        # Just call through to get_list.  The filtering is handled
        # in apply_request_kwargs. 
        #
        # This is defined as a separate method
        # to match the naming conventions expected by dispatch().  
        # We do this so dispatch() will do a separate check for allowed
        # methods.
        return self.get_list(request, **kwargs)

    def put_featured_list(self, request, **kwargs):
        story_id = kwargs.pop('story_id')
        story = Story.objects.get(story_id=story_id)
        self.is_authorized(request, story)
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        deserialized = self.alter_deserialized_list_data(request, deserialized)
        # Clear out existing relations
        story.featured_assets.clear()
        bundles = []
        asset_ids = [asset_data['asset_id'] for asset_data in deserialized]
        qs = self.get_object_list(request)
        assets = qs.filter(asset_id__in=asset_ids)
        for asset in assets:
            story.featured_assets.add(asset)
            bundles.append(self.build_bundle(obj=asset, request=request))
        story.save()

        if not self._meta.always_return_data:
            return http.HttpNoContent()
        else:
            to_be_serialized = {}
            to_be_serialized['objects'] = [self.full_dehydrate(bundle) for bundle in bundles]
            to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
            return self.create_response(request, to_be_serialized, response_class=http.HttpAccepted)

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
        if bundle.obj.asset_id and hasattr(bundle.obj, 'image'):
            try:
                image = Image.objects.get(localimageassettranslation__asset__asset_id=bundle.obj.asset_id)
                if image.file.url == bundle.data['image']:
                    bundle.data["image"] = image
                    return bundle
            except Exception:
                pass
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
        featured = kwargs.get('featured')
        if story_id:
            if featured:
                filters['featured_in_stories__story_id'] = story_id
            else:
                filters['stories__story_id'] = story_id

        if section_id:
            filters['sectionasset__section__section_id'] = section_id

        new_obj_list = obj_list.filter(**filters)

        if no_section and story_id:
            new_obj_list = new_obj_list.exclude(sectionasset__section__story__story_id=story_id)

        return new_obj_list

    def obj_get_list(self, request=None, **kwargs):
        """
        Get a list of assets, filtering based on the request's user and 
        the publication status
        
        """
        # Only show published assets 
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(owner=request.user)

        return super(AssetResource, self).obj_get_list(request, **kwargs).filter(q)

    def dehydrate(self, bundle):
        # Exclude the filename field from the output
        del bundle.data['filename']
        return bundle
    
    def dehydrate_content(self, bundle):
        return bundle.obj.render(format="html")

    def dehydrate_thumbnail_url(self, bundle):
        return bundle.obj.get_thumbnail_url(width=222, height=222)

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
    file = fields.FileField(attribute='file', blank=True, null=True)
    download_url = fields.CharField(attribute='download_url', readonly=True)
    # A "write-only" field for specifying the filename when uploading images
    # This is removed from responses to GET requests
    filename = fields.CharField(null=True)

    class Meta:
        always_return_data = True
        queryset = DataSet.objects.select_subclasses()
        resource_name = 'datasets'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'delete']
        authentication = Authentication()
        authorization = LoggedInAuthorization()
        validation = DataSetValidation()
        detail_uri_name = 'dataset_id'
        # Hide the underlying id
        excludes = ['id']

        delayed_authorization_methods = ['delete_detail']

    def detail_uri_kwargs(self, bundle_or_obj):
        """
        Given a ``Bundle`` or an object (typically a ``Model`` instance),
        it returns the extra kwargs needed to generate a detail URI.

        This version returns the dataset_id field instead of the pk
        """
        kwargs = {}

        if isinstance(bundle_or_obj, Bundle):
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.obj.dataset_id
        else:
            kwargs[self._meta.detail_uri_name] = bundle_or_obj.dataset_id

        return kwargs

    def get_object_class(self, bundle=None, request=None, **kwargs):
        if (bundle.data.get('file', None) or not bundle.data.get('url')):
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

    def obj_get_list(self, request=None, **kwargs):
        """
        Get a list of assets, filtering based on the request's user and 
        the publication status
        
        """
        # Only show published datasets 
        q = Q(status='published')
        if hasattr(request, 'user') and request.user.is_authenticated():
            # If the user is logged in, show their unpublished stories as
            # well
            q = q | Q(owner=request.user)
        return super(DataSetResource, self).obj_get_list(request, **kwargs).filter(q)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/(?P<dataset_id>[0-9a-f]{32,32})/upload%s$" %
                (self._meta.resource_name, trailing_slash()),
                DataSetFileUploadView.as_view(), 
                name="api_dispatch_upload"),
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

class UploadView(SingleObjectMixin, View):
    queryset = None
    translation_queryset = None
    obj_id_name = None
    translation_fk_name = None
    file_field_name = None
    file_model_class = None

    def get_object(self):
        """Retrieve the object by it's model specific id instead of pk"""
        queryset = self.get_queryset()
        obj_id = self.kwargs.get(self.obj_id_name, None)
        if obj_id is not None:
            filter_args = {self.obj_id_name: obj_id}
            queryset = queryset.filter(**filter_args)
            try:
                obj = queryset.get()
            except ObjectDoesNotExist:
                raise Http404(_(u"No %(verbose_name)s found matching the query") %
                        {'verbose_name': queryset.model._meta.verbose_name})
            if not obj.has_perm(self.request.user, 'change'):
                raise PermissionDenied(_(u"You are not authorized to edit this story"))
            return obj
        else:
            return None

    def get_translation_queryset(self):
        return self.translation_queryset

    def get_object_translation(self):
        queryset = self.get_translation_queryset()
        kwargs = {}
        kwargs[self.translation_fk_name] = self.object
        return queryset.get(**kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.has_perm(request.user, 'change'):
            return django_http.HttpResponsForbidden()
        file_field = self.file_field_name
        uploaded_file = request.FILES.get(file_field)
        if not uploaded_file:
            return django_http.HttpResponseBadRequest()
        file_model = self.file_model_class.objects.create(file=uploaded_file)
        if file_field in self.object.translated_fields:
            self.object_translation = self.get_object_translation()
            setattr(self.object_translation, file_field, file_model)
            self.object_translation.save()
        else:
            setattr(self.object, file_field, file_model)
            self.object.save()

        return django_http.HttpResponse("File successfully uploaded")

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(UploadView, self).dispatch(*args, **kwargs)

class AssetImageUploadView(UploadView):
    queryset = LocalImageAsset.objects.all()
    translation_queryset = LocalImageAssetTranslation.objects.all()
    obj_id_name = 'asset_id' 
    translation_fk_name = 'asset'
    file_field_name = 'image'
    file_model_class = Image

class DataSetFileUploadView(UploadView):
    queryset = LocalDataSet.objects.all()
    obj_id_name = 'dataset_id' 
    file_field_name = 'file'
    file_model_class = File 
