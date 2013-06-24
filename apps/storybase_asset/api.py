from django.conf.urls.defaults import url
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import UploadedFile

from tastypie import fields, http
from tastypie.authentication import Authentication
from tastypie.bundle import Bundle
from tastypie.exceptions import BadRequest, ImmediateHttpResponse, Unauthorized
from tastypie.utils import trailing_slash
from tastypie.validation import Validation

from filer.models import File, Image

from storybase.api import (DataUriResourceMixin,
   TranslatedModelResource, PublishedOwnerAuthorization)
from storybase_asset.models import (Asset, ExternalAsset, HtmlAsset, 
    LocalImageAsset, DataSet, ExternalDataSet, LocalDataSet)
from storybase_asset.utils import image_type_supported
from storybase_story.models import Story


class AssetResource(DataUriResourceMixin, TranslatedModelResource):
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
        authorization = PublishedOwnerAuthorization()
        # Hide the underlying id
        excludes = ['id']

        featured_list_allowed_methods = ['get', 'put']
        featured_detail_allowed_methods = []

    def get_object_class(self, bundle=None, **kwargs):
        if bundle and bundle.obj and bundle.obj.asset_id:
            return bundle.obj.__class__

        content_fields = ('body', 'image', 'url')
        num_content_fields = 0
        for name in content_fields:
            if bundle.data.get(name):
                num_content_fields = num_content_fields + 1
        if num_content_fields > 1:
            raise BadRequest("You must specify only one of the following fields: image, body, or url")
        if bundle.data.get('body'):
            return HtmlAsset
        elif bundle.data.get('url'):
            return ExternalAsset
        elif bundle.data.get('image'):
            return LocalImageAsset
        else:
            raise BadRequest("You must specify an image, body, or url") 


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
        try:
            self._meta.authorization.obj_has_perms(story, 
                    request.user, ['change']) 
        except Unauthorized, e:
            self.unauthorized_result(e)

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

    def post_detail(self, request, **kwargs):
        """
        Emulate put_detail in a very specific case

        The Tastypie docs describe the semantics of this method as
        "Creates a new subcollection of the resource under a resource"

        This isn't what we want, but we need to implement this
        method in order to support replacing an image asset's image
        in older browsers such as IE9. For the older browsers, we have to
        send the request via a form in a hidden IFRAME. We can use the
        PUT method with forms, so we have to use POST.
        """
        # Only support POST to the detail endpoint if we're making the
        # request from inside a hidden iframe 
        if not self.iframed_request(request):
            return http.HttpNotImplemented()

        # In the case of a POST from inside a hidden iframe, delegate
        # to put_detail
        return self.put_detail(request, **kwargs)

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

    def hydrate(self, bundle):
        """Manipulated data before all methods/fields have built out the hydrated data."""
        # If a DateTimeField field's data is passed as an empty string,
        # convert it to None.  
        # 
        # This is needed when doing a PUT using multipart/form-data as
        # the empty date/time fields are sent as empty strings instead of
        # ``null`` values.  They're passed as ``null`` values when the
        # PUT is sent JSON. If we don't convert the empty strings to None,
        # we get errors trying to convert an empty string to a datetime
        # object.
        for field in ['asset_created', 'published',]:
            if (field in bundle.data and
                isinstance(bundle.data[field], basestring) and
                len(bundle.data[field]) == 0):
                
                bundle.data[field] = None

        return bundle

    def hydrate_image(self, bundle):
        if bundle.obj.asset_id and hasattr(bundle.obj, 'image'):
            try:
                image = Image.objects.get(localimageassettranslation__asset__asset_id=bundle.obj.asset_id)
                if image.file.url == bundle.data['image']:
                    bundle.data["image"] = image
                    return bundle
            except Exception:
                pass

        if ('image' in bundle.data and
                isinstance(bundle.data['image'], UploadedFile)):
            # The image data is an uploaded file

            # Make sure the file format is supported
            if not image_type_supported(bundle.data['image']):
                raise BadRequest("Unsupported image format")

            # Create an image object and add it to the bundle
            image = Image.objects.create(file=bundle.data['image'])
            bundle.data['image'] = image
            return bundle 
        else:
            # Treat the image data as data-url-encoded
            # file
            return self._hydrate_file(bundle, Image, 'image', 'filename')

    def build_bundle(self, obj=None, data=None, request=None, objects_saved=None):
        if obj and obj.__class__ == Asset:
            # We don't have a subclass instance.  This is likely because
            # the object was retrieved through a RelatedField on another
            # resource
            obj = self._meta.queryset.get(asset_id=obj.asset_id)

        return super(AssetResource, self).build_bundle(obj, data, request, objects_saved)

    def obj_create(self, bundle, **kwargs):
        # Set the asset's owner to the request's user
        if bundle.request.user:
            kwargs['owner'] = bundle.request.user
        return super(AssetResource, self).obj_create(bundle, **kwargs)

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
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

class DataSetResource(DataUriResourceMixin, TranslatedModelResource):
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
        detail_allowed_methods = ['get', 'delete', 'put']
        authentication = Authentication()
        authorization = PublishedOwnerAuthorization()
        validation = DataSetValidation()
        detail_uri_name = 'dataset_id'
        # Hide the underlying id
        excludes = ['id']

        related_detail_allowed_methods = ['delete']

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

    def get_object_class(self, bundle=None, **kwargs):
        if bundle.data.get('file', None):
            return LocalDataSet
        elif bundle.data.get('url', None):
            return ExternalDataSet
        else:
            raise BadRequest("You must provide either a file or URL when creating a data set")

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        filters = {}
        story_id = kwargs.get('story_id')
        asset_id = kwargs.get('asset_id')

        if story_id:
            filters['stories__story_id'] = story_id

        if asset_id:
            filters['assets__asset_id'] = asset_id

        new_obj_list = obj_list.filter(**filters)

        return new_obj_list

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/assets/(?P<asset_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/stories/(?P<story_id>[0-9a-f]{32,32})/(?P<dataset_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_related_detail'), name="api_dispatch_related_detail"),
            url(r"^(?P<resource_name>%s)/assets/(?P<asset_id>[0-9a-f]{32,32})/(?P<dataset_id>[0-9a-f]{32,32})%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('dispatch_related_detail'), name="api_dispatch_related_detail"),
        ]

    def obj_create(self, bundle, **kwargs):
        story_id = kwargs.get('story_id')
        asset_id = kwargs.get('asset_id')

        if asset_id:
            try:
                asset = Asset.objects.get(asset_id=asset_id) 
                if not asset.has_perm(bundle.request.user, 'change'):
                    raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the asset matching the provided asset ID"))
            except ObjectDoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpNotFound("An asset matching the provided asset ID could not be found"))
        elif story_id:
            try:
                story = Story.objects.get(story_id=story_id) 
                if not story.has_perm(bundle.request.user, 'change'):
                    raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the story matching the provided story ID"))
            except ObjectDoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpNotFound("A story matching the provided story ID could not be found"))

        # Set the asset's owner to the request's user
        if bundle.request.user:
            kwargs['owner'] = bundle.request.user

        # Let the superclass create the object
        bundle = super(DataSetResource, self).obj_create(
            bundle, **kwargs)

        if asset_id:
            asset.datasets.add(bundle.obj)
        elif story_id:
            # Associate the newly created dataset with the story
            story.datasets.add(bundle.obj)

        return bundle

    def hydrate_file(self, bundle):
        if bundle.obj.dataset_id and hasattr(bundle.obj, 'file'):
            # The object is an existing model. Check if the
            # file attribute has changed, and if not, just
            # load the existing value
            try:
                f = File.objects.get(localdataset__dataset_id=bundle.obj.dataset_id)
                if f.file.url == bundle.data['file']:
                    bundle.data["file"] = f
                    return bundle
            except Exception:
                pass

        if ('file' in bundle.data and
            isinstance(bundle.data['file'], UploadedFile)):
            # The file data is an uploaded file, create a file object
            # and add it to the bundle
            file = File.objects.create(file=bundle.data['file'])
            bundle.data['file'] = file
            return bundle 
        else:
            # Treat the file data as data-url-encoded
            # file
            return self._hydrate_file(bundle, File, 'file', 'filename')

    def dehydrate(self, bundle):
        # Exclude the filename field from the output
        del bundle.data['filename']
        return bundle

    def dispatch_related_detail(self, request, **kwargs):
        # This is defined as a separate method
        # so dispatch will check which method is allowed separately
        # from the other method handlers
        return self.dispatch('related_detail', request, **kwargs)

    def delete_related_detail(self, request, **kwargs):
        bundle = Bundle(request=request)
        dataset_id = kwargs.get('dataset_id')
        story_id = kwargs.pop('story_id', None)
        asset_id = kwargs.pop('asset_id', None)

        if asset_id:
            try:
                asset = Asset.objects.get(asset_id=asset_id) 
                if not asset.has_perm(bundle.request.user, 'change'):
                    raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the asset matching the provided asset ID"))
            except ObjectDoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpNotFound("An asset matching the provided asset ID could not be found"))
        elif story_id:
            try:
                story = Story.objects.get(story_id=story_id) 
                if not story.has_perm(bundle.request.user, 'change'):
                    raise ImmediateHttpResponse(response=http.HttpUnauthorized("You are not authorized to change the story matching the provided story ID"))
            except ObjectDoesNotExist:
                raise ImmediateHttpResponse(response=http.HttpNotFound("A story matching the provided story ID could not be found"))

        self.obj_get(bundle, dataset_id=dataset_id)

        if asset_id:
            asset.datasets.remove(bundle.obj)
        elif story_id:
            story.datasets.remove(bundle.obj)

        return http.HttpNoContent()
