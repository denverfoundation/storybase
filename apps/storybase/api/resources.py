from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.dispatch import receiver, Signal
from django.http import HttpResponse

from tastypie import fields, http
from tastypie.bundle import Bundle
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.resources import (ModelResource, convert_post_to_put, 
                                convert_post_to_patch, NOT_AVAILABLE)

# Signals sent by HookedModelResource
post_bundle_obj_construct = Signal(providing_args=["bundle", "request"])
"""Signal sent after the object is constructed, but not saved"""
pre_bundle_obj_hydrate = Signal(providing_args=["bundle", "request"])
"""Signal sent before the bundle is hydrated"""
post_bundle_obj_hydrate = Signal(providing_args=["bundle", "request"])
"""Signal sent after the bundle is hydrated"""
post_bundle_obj_save = Signal(providing_args=["bundle", "request"])
"""Signal sent after the bundle is saved"""
post_obj_get = Signal(providing_args=["request", "object"])

class HookedModelResource(ModelResource):
    """
    A version of ModelResource with extra actions at various points in the pipeline
    
    This allows for doing things like creating related translation model
    instances or doing row-level authorization checks in a DRY way since
    most of the logic for the core logic of the request/response cycle
    remains the same as ModelResource.

    The hooks are implemented using Django's signal framework.  In this case
    the resource is sending a signal to itself and the signal handlers
    are defined as methods of the HookedModelResource subclass.  Because
    of this, the signature for these methods has an initial argument of
    sender instead of the conventional self, even though its referring
    to the resource object.

    """
    def _bundle_setattr(self, bundle, key, value):
        setattr(bundle.obj, key, value)

    def get_object_class(self, bundle=None, request=None, **kwargs):
        """Get the resource's object class dynamically
        
        By default just returns ``object_class`` as defined in the resource
        declaration, but this can be overridden in subclasses to do something
        more interesting.

        """
        return self._meta.object_class

    def full_hydrate(self, bundle):
        """
        Given a populated bundle, distill it and turn it back into
        a full-fledged object instance.
        """
        if bundle.obj is None:
            bundle.obj = self._meta.object_class()
            post_bundle_obj_construct.send(sender=self, bundle=bundle, request=None) 
        bundle = self.hydrate(bundle)
        post_bundle_obj_hydrate.send(sender=self, bundle=bundle, request=None)
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
                        self._bundle_setattr(bundle, field_object.attribute, value)
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
        post_bundle_obj_construct.send(sender=self, bundle=bundle, request=request, **kwargs)

        for key, value in kwargs.items():
            self._bundle_setattr(bundle, key, value)
        pre_bundle_obj_hydrate.send(sender=self, bundle=bundle, request=request, **kwargs)
        bundle = self.full_hydrate(bundle)
        self.is_valid(bundle,request)

        if bundle.errors:
            self.error_response(bundle.errors, request)

        # Save FKs just in case.
        self.save_related(bundle)

        # Save parent
        bundle.obj.save()
        post_bundle_obj_save.send(sender=self, bundle=bundle, request=request, **kwargs)

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
                post_bundle_obj_construct.send(sender=self, bundle=bundle, request=request, **kwargs)
                bundle.data.update(kwargs)
                bundle = self.full_hydrate(bundle)
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
        post_bundle_obj_save.send(sender=self, bundle=bundle, request=request, **kwargs)

        # Now pick up the M2M bits.
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        return bundle

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

        # Send a signal
        post_obj_get.send(sender=self, request=request, obj=obj)

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
            self.is_authorized(request)
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

    @receiver(pre_bundle_obj_hydrate)
    def check_bundle_obj_authorization(sender, bundle, request, **kwargs):
        """
        Check authorization of the bundle's object
        
        Simply calls through to is_authorized.

        This should be connected to the ``pre_bundle_obj_hydrate`` signal.

        """
        sender.is_authorized(request, bundle.obj)

    @receiver(post_obj_get)
    def check_obj_authorization(sender, request, obj, **kwargs):
        """
        Check authorization of an object based on the request

        Simply calls through to the is_authorized method of the resource

        This should be connected to the ``post_obj_get`` signal.

        """
        sender.is_authorized(request, obj)


class TranslatedModelResource(HookedModelResource):
    """A version of ModelResource that handles our translation implementation"""
    # This is a write-only field that we include to allow specifying the
    # language when creating an object.  We remove it from the response in
    # dehydrate()
    language = fields.CharField(attribute='language', default=settings.LANGUAGE_CODE)
    languages = fields.ListField(readonly=True)

    def dehydrate(self, bundle):
        # Remove the language field since it doesn't make sense in the response
        del bundle.data['language']
        return bundle

    def dehydrate_languages(self, bundle):
        return bundle.obj.get_language_info()

    @receiver(post_bundle_obj_construct)
    def translation_obj_construct(sender, bundle, request, **kwargs):
        """
        Create a translation object and add it to the bundle
        
        This should be connected to the ``post_bundle_obj_construct`` signal

        """
        object_class = sender.get_object_class(bundle, request, **kwargs)
        translation_class = object_class.translation_class
        bundle.translation_obj = translation_class()

    @receiver(post_bundle_obj_save)
    def translation_obj_save(sender, bundle, request, **kwargs):
        """
        Associate the translation object with its parent and save

        This should be connected to the ``post_bundle_obj_save`` signal

        """
        object_class = sender._meta.object_class
        # Associate and save the translation
        fk_field_name = object_class.get_translation_fk_field_name()
        setattr(bundle.translation_obj, fk_field_name, bundle.obj)
        bundle.translation_obj.save()

    @receiver(post_bundle_obj_hydrate)
    def translation_obj_get(sender, bundle, request, **kwargs):
        """
        Get the associated translation model instance

        This should be connected to the ``post_bundle_obj_hydrate``
        signal.

        """
        if bundle.obj.pk and not hasattr(bundle, 'translation_obj'):
            language = bundle.data.get('language', sender.fields['language'].default)
            translation_set = getattr(bundle.obj, bundle.obj.translation_set)
            bundle.translation_obj = translation_set.get(language=language)

    def _get_translation_fields(self, bundle):
        object_class = self.get_object_class(bundle)
        return object_class.translated_fields + ['language']

    def _bundle_setattr(self, bundle, key, value):
        if not hasattr(bundle, 'translation_fields'):
            bundle.translation_fields = self._get_translation_fields(bundle) 

        if key in bundle.translation_fields: 
            setattr(bundle.translation_obj, key, value)
        else:
            setattr(bundle.obj, key, value)


