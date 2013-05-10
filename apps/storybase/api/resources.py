"""Base Resource classes for Tastypie-based API"""

# Significant portions of this code are based on Tastypie
# (http://tastypieapi.org)
# 
# This is mostly because I had to patch methods in the Tastypie API
# to provide additional hooks or workarounds.
#
# Tastypie's license is as follows:
#
# Copyright (c) 2010, Daniel Lindsley
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the tastypie nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL tastypie BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from cStringIO import StringIO
import base64
import os
import re

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse

from tastypie import fields, http
from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.resources import (ModelResource, 
                                convert_post_to_patch)
from tastypie.utils import dict_strip_unicode_keys
from tastypie.utils.mime import build_content_type

class MultipartFileUploadModelResource(ModelResource):
    """
    A version of ModelResource that accepts file uploads via
    multipart forms.

    Based on Work by Michael Wu and Philip Smith. 
    See https://github.com/toastdriven/django-tastypie/pull/606

    This resource class also supports wrapping a serialized response in
    a TEXTAREA element for use with the jQuery IFRAME Transport.  See
    http://cmlenz.github.com/jquery-iframe-transport/

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

    def put_detail(self, request, **kwargs):
        """
        Either updates an existing resource or creates a new one with the
        provided data.

        Calls ``obj_update`` with the provided data first, but falls back to
        ``obj_create`` if the object does not already exist.

        If a new resource is created, return ``HttpCreated`` (201 Created).
        If ``Meta.always_return_data = True``, there will be a populated body
        of serialized data.

        If an existing resource is modified and
        ``Meta.always_return_data = False`` (default), return ``HttpNoContent``
        (204 No Content).
        If an existing resource is modified and
        ``Meta.always_return_data = True``, return ``HttpAccepted`` (202
        Accepted).
        """
        fmt = request.META.get('CONTENT_TYPE', 'application/json')
        if fmt.startswith('multipart'):
            body = None
        elif django.VERSION >= (1, 4):
            body = request.body
        else:
            body = request.raw_post_data
        deserialized = self.deserialize(request, body, format=fmt)
        deserialized = self.alter_deserialized_detail_data(request, deserialized)
        bundle = self.build_bundle(data=dict_strip_unicode_keys(deserialized), request=request)

        try:
            updated_bundle = self.obj_update(bundle=bundle, **self.remove_api_resource_names(kwargs))

            if not self._meta.always_return_data:
                return http.HttpNoContent()
            else:
                updated_bundle = self.full_dehydrate(updated_bundle)
                updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
                return self.create_response(request, updated_bundle, response_class=http.HttpAccepted)
        except (NotFound, MultipleObjectsReturned):
            updated_bundle = self.obj_create(bundle=bundle, **self.remove_api_resource_names(kwargs))
            location = self.get_resource_uri(updated_bundle)

            if not self._meta.always_return_data:
                return http.HttpCreated(location=location)
            else:
                updated_bundle = self.full_dehydrate(updated_bundle)
                updated_bundle = self.alter_detail_data_to_serialize(request, updated_bundle)
                return self.create_response(request, updated_bundle, response_class=http.HttpCreated, location=location)

    def iframed_request(self, request):
        """
        Checks if the request was issued from an IFRAME
        
        When being called from an IFRAME, an ``iframe`` parameter should be
        added to the querystring.

        """
        if not request:
            return False

        return 'iframe' in request.GET

    def wrap_in_textarea(self, format, body):
        """
        Wrap response text in a textarea
        
        This allows the jQuery Iframe transport to detect the content type.

        """
        return '<textarea data-type="%s">%s</textarea>' % (format, body)

    def serialize(self, request, data, format, options=None):
        serialized = super(MultipartFileUploadModelResource, self).serialize(
                           request, data, format, options)
        if not self.iframed_request(request):
            return serialized
        else:
            return self.wrap_in_textarea(format, serialized)

    def build_content_type(self, request, desired_format):
        """Always return 'text/html' when the request is from an IFRAME"""
        if self.iframed_request(request):
            return 'text/html'

        return build_content_type(desired_format) 

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        This version overrides the content type header to be 'text/html' if
        the request originates from an IFRAME.

        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        content_type = self.build_content_type(request, desired_format)
        return response_class(content=serialized, content_type=content_type, **response_kwargs)


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

    def get_object_class(self, bundle=None, **kwargs):
        """Get the resource's object class dynamically
        
        By default just returns ``object_class`` as defined in the resource
        declaration, but this can be overridden in subclasses to do something
        more interesting.

        """
        return self._meta.object_class

    def post_bundle_obj_construct(self, bundle, **kwargs):
        """Hook executed after the object is constructed, but not saved"""
        pass

    def pre_bundle_obj_hydrate(self, bundle, **kwargs):
        """Hook executed before the bundle is hydrated"""
        pass

    def post_bundle_obj_hydrate(self, bundle):
        """Hook executed after the bundle is hydrated"""
        pass

    def post_bundle_obj_save(self, bundle, **kwargs):
        """Hook executed after the bundle is saved"""
        pass

    def post_bundle_obj_get(self, bundle):
        """Hook executed after the object is retrieved"""
        pass

    def post_obj_get(self, obj, **kwargs):
        pass

    def post_full_hydrate(self, obj, **kwargs):
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

    def save(self, bundle, skip_errors=False, **kwargs):
        self.is_valid(bundle)

        if bundle.errors and not skip_errors:
            raise ImmediateHttpResponse(response=self.error_response(bundle.request, bundle.errors))

        # Check if they're authorized.
        if bundle.obj.pk:
            self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        else:
            self.authorized_create_detail(self.get_object_list(bundle.request), bundle)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save the main object.
        bundle.obj.save()
        self.post_bundle_obj_save(bundle, **kwargs)
        bundle.objects_saved.add(self.create_identifier(bundle.obj))

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

    def obj_create(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_create``.
        """
        object_class = self.get_object_class(bundle, **kwargs)
        bundle.obj = object_class()
        self.post_bundle_obj_construct(bundle, **kwargs)

        for key, value in kwargs.items():
            self.bundle_obj_setattr(bundle, key, value)

        self.authorized_create_detail(self.get_object_list(bundle.request), bundle)
        self.pre_bundle_obj_hydrate(bundle, **kwargs)
        bundle = self.full_hydrate(bundle)
        self.post_full_hydrate(bundle, **kwargs)
        return self.save(bundle)

    def lookup_kwargs_with_identifiers(self, bundle, kwargs):
        """
        Kwargs here represent uri identifiers Ex: /repos/<user_id>/<repo_name>/
        We need to turn those identifiers into Python objects for generating
        lookup parameters that can find them in the DB
        """
        lookup_kwargs = {}
        bundle.obj = self.get_object_list(bundle.request).model()
        self.post_bundle_obj_construct(bundle, **kwargs)
        # Override data values, we rely on uri identifiers
        bundle.data.update(kwargs)
        # We're going to manually hydrate, as opposed to calling
        # ``full_hydrate``, to ensure we don't try to flesh out related
        # resources & keep things speedy.
        bundle = self.hydrate(bundle)

        for identifier in kwargs:
            if identifier == self._meta.detail_uri_name:
                lookup_kwargs[identifier] = kwargs[identifier]
                continue

            field_object = self.fields[identifier]

            # Skip readonly or related fields.
            if field_object.readonly is True or getattr(field_object, 'is_related', False):
                continue

            # Check for an optional method to do further hydration.
            method = getattr(self, "hydrate_%s" % identifier, None)

            if method:
                bundle = method(bundle)

            if field_object.attribute:
                value = field_object.hydrate(bundle)

            lookup_kwargs[identifier] = value

        return lookup_kwargs

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        """
        A ORM-specific implementation of ``obj_update``.
        """
        if not bundle.obj or not self.get_bundle_detail_data(bundle):
            try:
                lookup_kwargs = self.lookup_kwargs_with_identifiers(bundle, kwargs)
            except:
                # if there is trouble hydrating the data, fall back to just
                # using kwargs by itself (usually it only contains a "pk" key
                # and this will work fine.
                lookup_kwargs = kwargs

            try:
                bundle.obj = self.obj_get(bundle, **lookup_kwargs)
                self.post_obj_get(bundle.obj)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        self.authorized_update_detail(self.get_object_list(bundle.request), bundle)
        bundle = self.full_hydrate(bundle)
        self.post_full_hydrate(bundle, **kwargs)
        return self.save(bundle, skip_errors=skip_errors)

    def obj_delete(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
                self.post_obj_get(bundle.obj)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")

        self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
        bundle.obj.delete()

    def patch_detail(self, request, **kwargs):
        """
        Updates a resource in-place.

        Calls ``obj_update``.

        If the resource is updated, return ``HttpAccepted`` (202 Accepted).
        If the resource did not exist, return ``HttpNotFound`` (404 Not Found).
        """
        request = convert_post_to_patch(request)
        basic_bundle = self.build_bundle(request=request)

        # We want to be able to validate the update, but we can't just pass
        # the partial data into the validator since all data needs to be
        # present. Instead, we basically simulate a PUT by pulling out the
        # original data and updating it in-place.
        # So first pull out the original object. This is essentially
        # ``get_detail``.
        try:
            obj = self.cached_obj_get(bundle=basic_bundle, **self.remove_api_resource_names(kwargs))
        except ObjectDoesNotExist:
            return http.HttpNotFound()
        except MultipleObjectsReturned:
            return http.HttpMultipleChoices("More than one resource is found at this URI.")

        self.post_obj_get(obj)

        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle)
        bundle = self.alter_detail_data_to_serialize(request, bundle)

        # Now update the bundle in-place.
        deserialized = self.deserialize(request, request.raw_post_data, format=request.META.get('CONTENT_TYPE', 'application/json'))
        self.update_in_place(request, bundle, deserialized)
        # TODO: Check if this try/except is neccessary
        #try:
        #    self.update_in_place(request, bundle, deserialized)
        #except ObjectDoesNotExist:
        #    return http.HttpNotFound()
        #

        if not self._meta.always_return_data:
            return http.HttpAccepted()
        else:
            bundle = self.full_dehydrate(bundle)
            bundle = self.alter_detail_data_to_serialize(request, bundle)
            return self.create_response(request, bundle, response_class=http.HttpAccepted)

    def apply_request_kwargs(self, obj_list, bundle, **kwargs):
        """
        Hook for altering the default object list based on keyword
        arguments
        """
        return obj_list

    def obj_get_list(self, bundle, **kwargs):
        """
        Modify the default queryset based on keyword arguments
        """
        obj_list = super(HookedModelResource, self).obj_get_list(bundle, **kwargs)
        return self.apply_request_kwargs(obj_list, bundle, **kwargs)


class TranslatedModelResource(HookedModelResource):
    """A version of ModelResource that handles our translation implementation"""
    language = fields.CharField(attribute='language', default=settings.LANGUAGE_CODE)
    languages = fields.ListField(readonly=True)

    def dehydrate_languages(self, bundle):
        return bundle.obj.get_language_info()

    def post_bundle_obj_construct(self, bundle, **kwargs):
        """
        Create a translation object and add it to the bundle
        """
        object_class = self.get_object_class(bundle, **kwargs)
        translation_class = object_class.translation_class
        bundle.translation_obj = translation_class()

    def post_bundle_obj_save(self, bundle, **kwargs):
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

    def post_bundle_obj_hydrate(self, bundle):
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

    def patch_detail(self, request, **kwargs):
        try:
            return super(TranslatedModelResource, self).patch_detail(request, **kwargs)
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
