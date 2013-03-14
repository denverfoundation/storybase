from cStringIO import StringIO
import base64
import os
import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse

from tastypie import fields, http
from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.resources import (ModelResource, convert_post_to_put, 
                                convert_post_to_patch, NOT_AVAILABLE)

class MultipartFileUploadModelResource(ModelResource):
    """
    A version of ModelResource that accepts file uploads via
    multipart forms.

    Based on Work by Michael Wu and Philip Smith. 
    See https://github.com/toastdriven/django-tastypie/pull/606

    """
    def deserialize(self, request, data, format='application/json'):
        """
        Given a request, data and a format, deserializes the given data.

        It relies on the request properly sending a ``CONTENT_TYPE`` header,
        falling back to ``application/json`` if not provided.

        Mostly a hook, this uses the ``Serializer`` from ``Resource._meta``.
        """
        # If the format of the request is 
        # or multipart/form-data, then ignore the data attribute and
        # just grab the data to deserialize from the request
        if format.startswith('multipart'):
            deserialized = request.POST.copy()
            deserialized.update(request.FILES)
        else:
            deserialized = self._meta.serializer.deserialize(data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        return deserialized


class HookedModelResource(MultipartFileUploadModelResource):
    """
    A version of ModelResource with extra actions at various points in 
    the pipeline
    
    This allows for doing things like creating related translation model
    instances or doing row-level authorization checks in a DRY way since
    most of the logic for the core logic of the request/response cycle
    remains the same as ModelResource.

    """
    def bundle_obj_setattr(self, bundle, key, value):
        """Hook for setting attributes of the bundle's object

        This is useful if additional bundle objects also need to be modified
        in addition to the core object.

        """
        setattr(bundle.obj, key, value)

    def get_object_class(self, bundle=None, request=None, **kwargs):
        """Get the resource's object class dynamically
        
        By default just returns ``object_class`` as defined in the resource
        declaration, but this can be overridden in subclasses to do something
        more interesting.

        """
        return self._meta.object_class

    def post_bundle_obj_construct(self, bundle, request=None, **kwargs):
        """Hook executed after the object is constructed, but not saved"""
        pass

    def pre_bundle_obj_hydrate(self, bundle, request=None, **kwargs):
        """Hook executed before the bundle is hydrated"""
        pass

    def post_bundle_obj_hydrate(self, bundle, request=None):
        """Hook executed after the bundle is hydrated"""
        pass

    def post_bundle_obj_save(self, bundle, request=None, **kwargs):
        """Hook executed after the bundle is saved"""
        pass

    def post_bundle_obj_get(self, bundle, request=None):
        """Hook executed after the object is retrieved"""
        pass

    def post_obj_get(self, obj, request=None, **kwargs):
        pass

    def post_full_hydrate(self, obj, request=None, **kwargs):
        pass

    def full_hydrate(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        if bundle.obj is None:
            bundle.obj = self._meta.object_class()
            self.post_bundle_obj_construct(bundle)
        bundle = self.hydrate(bundle)
        self.post_bundle_obj_hydrate(bundle)
        for field_name, field_object in self.fields.items():
            if field_object.readonly is True:
                continue

            # Check for an optional method to do further hydration.
            method = getattr(self, "hydrate_%s" % field_name, None)

            if method:
                bundle = method(bundle)
            if field_object.attribute:
                value = field_object.hydrate(bundle)

                # NOTE: We only get back a bundle when it is related field.
                if isinstance(value, Bundle) and value.errors.get(field_name):
                    bundle.errors[field_name] = value.errors[field_name]

                if value is not None or field_object.null:
                    # We need to avoid populating M2M data here as that will
                    # cause things to blow up.
                    if not getattr(field_object, 'is_related', False):
                        self.bundle_obj_setattr(bundle, field_object.attribute, value)
                    elif not getattr(field_object, 'is_m2m', False):
                        if value is not None:
                            setattr(bundle.obj, field_object.attribute, value.obj)
                        elif field_object.blank:
                            continue
                        elif field_object.null:
                            setattr(bundle.obj, field_object.attribute, value)

        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """

        object_class = self.get_object_class(bundle, request, **kwargs)
        bundle.obj = object_class()
        self.post_bundle_obj_construct(bundle, request, **kwargs)

        for key, value in kwargs.items():
            self.bundle_obj_setattr(bundle, key, value)
        self.pre_bundle_obj_hydrate(bundle, request, **kwargs)
        bundle = self.full_hydrate(bundle)
        self.post_full_hydrate(bundle, request, **kwargs)
        self.is_valid(bundle,request)

        if bundle.errors:
            self.error_response(bundle.errors, request)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save parent
        bundle.obj.save()
        self.post_bundle_obj_save(bundle, request, **kwargs)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def obj_update(self, bundle, request=None, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        if not bundle.obj or not bundle.obj.pk:
            # Attempt to hydrate data from kwargs before doing a lookup for the object.
            # This step is needed so certain values (like datetime) will pass model validation.
            try:
                bundle.obj = self.get_object_list(bundle.request).model()
                self.post_bundle_obj_construct(bundle, request, **kwargs)
                bundle.data.update(kwargs)
                bundle = self.full_hydrate(bundle)
                self.post_full_hydrate(bundle, request, **kwargs)
                lookup_kwargs = kwargs.copy()

                for key in kwargs.keys():
                    if key == 'pk':
                        continue
                    elif getattr(bundle.obj, key, NOT_AVAILABLE) is not NOT_AVAILABLE:
                        lookup_kwargs[key] = getattr(bundle.obj, key)
                    else:
                        del lookup_kwargs[key]
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle.request, **lookup_kwargs)
                self.post_obj_get(bundle.obj, request)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        bundle = self.full_hydrate(bundle)
        self.is_valid(bundle,request)

        if bundle.errors and not skip_errors:
            self.error_response(bundle.errors, request)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()
        self.post_bundle_obj_save(bundle, request, **kwargs)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def obj_delete(self, request=None, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        obj = kwargs.pop('_obj', None)

        if not hasattr(obj, 'delete'):
            try:
                obj = self.obj_get(request, **kwargs)
                self.post_obj_get(obj, request)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        obj.delete()

    def patch_detail(self, request, **kwargs):
        """
        Updates a resource in-place.

        Calls ``obj_update``.

        If the resource is updated, return ``HttpAccepted`` (202 Accepted).
        If the resource did not exist, return ``HttpNotFound`` (404 Not Found).
        """
        request = convert_post_to_patch(request)

        # We want to be able to validate the update, but we can't just pass
        # the partial data into the validator since all data needs to be
        # present. Instead, we basically simulate a PUT by pulling out the
        # original data and updating it in-place.
        # So first pull out the original object. This is essentially
        # ``get_detail``.
        try:
            obj = self.cached_obj_get(request=request, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        self.post_obj_get(obj, request)

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)

        # Now update the bundle in-place.
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        try:
            self.update_in_place(request, bundle, deserialized)
        except ObjectDoesNotExist:
            return http.HttpNotFound()

        if not self._meta.always_return_data:
            return http.HttpAccepted()
        else:
            bundle = self.full_dehydrate(bundle)
            bundle = self.alter_detail_data_to_serialize(request, bundle)
            return self.create_response(request, bundle, response_class=http.HttpAccepted)

    def apply_request_kwargs(self, obj_list, request, **kwargs):
        """
        Hook for altering the default object list based on keyword
        arguments
        """
        return obj_list

    def obj_get_list(self, request=None, **kwargs):
        """
        Modify the default queryset based on keyword arguments
        """
        obj_list = super(HookedModelResource, self).obj_get_list(request, **kwargs)
        return self.apply_request_kwargs(obj_list, request, **kwargs)

    def is_authorized(self, request, object=None, **kwargs):
        """
        Handles checking of permissions to see if the user has authorization
        to GET, POST, PUT, or DELETE this resource.  If ``object`` is provided,
        the authorization backend can apply additional row-level permissions
        checking.

        This version also takes the keyword arguments.  It doesn't do
        anything with them, but this could be implemented in a subclass
        to check authorization based on the arguments.
        """
        super(HookedModelResource, self).is_authorized(request, object)

    def dispatch(self, request_type, request, **kwargs):
        """
        Handles the common operations (allowed HTTP method, authentication,
        throttling, method lookup) surrounding most CRUD interactions.

        This version passes the keyword arguments to the authorization
        method.
        """
        allowed_methods = getattr(self._meta, "%s_allowed_methods" % request_type, None)
        request_method = self.method_check(request, allowed=allowed_methods)
        method = getattr(self, "%s_%s" % (request_method, request_type), None)

        if method is None:
            raise ImmediateHttpResponse(response=http.HttpNotImplemented())

        self.is_authenticated(request)
        self.is_authorized(request, **kwargs)
        self.throttle_check(request)

        # All clear. Process the request.
        request = convert_post_to_put(request)
        response = method(request, **kwargs)

        # Add the throttled request.
        self.log_throttled_access(request)

        # If what comes back isn't a ``HttpResponse``, assume that the
        # request was accepted and that some action occurred. This also
        # prevents Django from freaking out.
        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response


class DelayedAuthorizationResource(HookedModelResource):
    def dispatch(self, request_type, request, **kwargs):
        """
        Handles the common operations (allowed HTTP method, authentication,
        throttling, method lookup) surrounding most CRUD interactions.

        This version moves the authorization check to later in the pipeline
        """
        allowed_methods = getattr(self._meta, "%s_allowed_methods" % request_type, None)
        request_method = self.method_check(request, allowed=allowed_methods)
        method_name = "%s_%s" % (request_method, request_type)
        method = getattr(self, method_name, None)

        if method is None:
            raise ImmediateHttpResponse(response=http.HttpNotImplemented())

        self.is_authenticated(request)
        if method_name not in self._meta.delayed_authorization_methods:
            self.is_authorized(request, **kwargs)
        self.throttle_check(request)

        # All clear. Process the request.
        request = convert_post_to_put(request)
        response = method(request, **kwargs)

        # Add the throttled request.
        self.log_throttled_access(request)

        # If what comes back isn't a ``HttpResponse``, assume that the
        # request was accepted and that some action occurred. This also
        # prevents Django from freaking out.
        if not isinstance(response, HttpResponse):
            return http.HttpNoContent()

        return response

    def pre_bundle_obj_hydrate(self, bundle, request=None, **kwargs):
        """
        Check authorization of the bundle's object
        
        Simply calls through to is_authorized.
        """
        self.is_authorized(request, bundle.obj, **kwargs)

    def post_obj_get(self, obj, request=None, **kwargs):
        """
        Check authorization of an object based on the request

        Simply calls through to the is_authorized method of the resource
        """
        self.is_authorized(request, obj, **kwargs)


class TranslatedModelResource(HookedModelResource):
    """A version of ModelResource that handles our translation implementation"""
    language = fields.CharField(attribute='language', default=settings.LANGUAGE_CODE)
    languages = fields.ListField(readonly=True)

    def dehydrate_languages(self, bundle):
        return bundle.obj.get_language_info()

    def post_bundle_obj_construct(self, bundle, request=None, **kwargs):
        """
        Create a translation object and add it to the bundle
        """
        object_class = self.get_object_class(bundle, request, **kwargs)
        translation_class = object_class.translation_class
        bundle.translation_obj = translation_class()

    def post_bundle_obj_save(self, bundle, request, **kwargs):
        """
        Associate the translation object with its parent and save
        """
        object_class = self._meta.object_class
        fk_field_name = object_class.get_translation_fk_field_name()
        setattr(bundle.translation_obj, fk_field_name, bundle.obj)
        bundle.translation_obj.save()
        # Update the translation object cache in the bundle object
        # so further steps will get our fresh data
        bundle.obj.set_translation_cache_item(bundle.translation_obj.language, bundle.translation_obj)

    def post_bundle_obj_hydrate(self, bundle, request=None):
        """
        Get the associated translation model instance
        """
        if bundle.obj.pk:
            language = bundle.data.get('language', self.fields['language'].default)
            translation_set = getattr(bundle.obj, bundle.obj.translation_set)
            bundle.translation_obj = translation_set.get(language=language)

    def _get_translation_fields(self, bundle):
        object_class = self.get_object_class(bundle)
        return object_class.translated_fields + ['language']

    def bundle_obj_setattr(self, bundle, key, value):
        if not hasattr(bundle, 'translation_fields'):
            bundle.translation_fields = self._get_translation_fields(bundle) 

        if key in bundle.translation_fields: 
            setattr(bundle.translation_obj, key, value)
        else:
            setattr(bundle.obj, key, value)

    def put_detail(self, request, **kwargs):
        try:
            return super(TranslatedModelResource, self).put_detail(request, **kwargs)
        except ObjectDoesNotExist:
            return http.HttpNotFound()


class DataUriResourceMixin(object):
    def parse_data_uri(self, data_uri):
        """
        Parse a data URI string

        Returns a tuple of (mime_type, encoding, data) represented in the URI
        
        See http://tools.ietf.org/html/rfc2397

        """
        pattern = r"data:(?P<mime>[\w/]+);(?P<encoding>\w+),(?P<data>.*)"
        m = re.search(pattern, data_uri)
        return (m.group('mime'), m.group('encoding'), m.group('data'))

    def _hydrate_file(self, bundle, file_model_class, file_field, 
        filename_field='filename'):
        """Decode the base-64 encoded file"""
        def file_size(f):
            f.seek(0, os.SEEK_END)
            return f.tell()

        file_uri = bundle.data.get(file_field, None)

        if file_uri:
            (content_type, encoding, data) = self.parse_data_uri(
                file_uri)
            filename = bundle.data.get(filename_field)
            f = StringIO()
            f.write(base64.b64decode(data))
            size = file_size(f)
            file = InMemoryUploadedFile(file=f, field_name=None, 
                                        name=filename,
                                        content_type=content_type,
                                        size=size, charset=None)
            file_model = file_model_class.objects.create(file=file)
            bundle.data[file_field] = file_model 
            f.close()

        return bundle
