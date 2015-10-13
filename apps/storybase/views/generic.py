""""Common generic views"""
import os.path

try:
    import shortuuid
except ImportError:
    shortuuid = None

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseNotFound
from django.shortcuts import redirect
from django.template import loader, RequestContext
from django.views.generic import DetailView
from django.utils.translation import get_language, ugettext as _

class ModelIdDetailView(DetailView):
    """DetailView that retrieves objects by custom id instead of pk"""
    def dispatch(self, *args, **kwargs):
        return super(ModelIdDetailView, self).dispatch(*args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        """Handle language-aware paths"""
        obj = context.get(self.context_object_name)
        if hasattr(obj, 'get_languages'):
            language_code = get_language()
            available_languages = obj.get_languages()
            if language_code not in available_languages:
                alt_lang = settings.LANGUAGE_CODE
                if alt_lang not in available_languages:
                    alt_lang = available_languages[0]
                path = obj.get_absolute_url()
                return redirect('/%s%s' % (alt_lang, path))

        return super(ModelIdDetailView, self).render_to_response(
            context, **response_kwargs)

    def get_object_id_name(self):
        """Retrieve the name of the object's custom id field"""
        queryset = self.get_queryset()
        model_name = queryset.model._meta.model_name
        return '%s_id' % model_name

    def get_short_object_id_name(self):
        return 'short_%s' % (self.get_object_id_name())

    def get_short_object_id(self):
        if not shortuuid:
            return None

        short_obj_id_name = self.get_short_object_id_name()
        short_obj_id = self.kwargs.get(short_obj_id_name, None)

        if short_obj_id is None:
            return None 

        return shortuuid.decode(short_obj_id).hex

    def get_object_id(self):
        obj_id_name = self.get_object_id_name() 
        obj_id = self.kwargs.get(obj_id_name, None)
        if obj_id is None:
            obj_id = self.get_short_object_id()

        return obj_id_name, obj_id

    def get_object(self):
        """Retrieve the object by it's model specific id instead of pk"""
        queryset = self.get_queryset()
        obj_id_name, obj_id = self.get_object_id()
        slug = self.kwargs.get('slug', None)

        if slug is not None:
            queryset = queryset.filter(slug=slug)
        elif obj_id is not None:
            filter_args = {obj_id_name: obj_id}
            queryset = queryset.filter(**filter_args)
        else:
            raise AssertionError("%s must be called with "
                                 "either a object %s or slug" % 
                                 (self.__class__.__name__, obj_id_name))

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(
                _(u"No %(verbose_name)s found matching the query") %
		       {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class VersionTemplateMixin(object):
    """Class-based view mixin that searches for a versioned template name"""
    def get_versioned_template_names(self, template_names, version):
        versioned_names = []
        for template_name in template_names: 
            (head, tail) = os.path.split(template_name)
            (template_name_base, extension) = tail.split('.')
            versioned_names.append(
                os.path.join(head, "%s-%s.%s" % (template_name_base, version, extension)))
        return versioned_names + template_names

    def get_template_names(self):
        """
        Returns a list of template names to search for when rendering the template.

        By default, the list of template names contains the value of the
        ``template_name`` attribute of the view class.

        If ``version`` is one the keyword arguments captured from the URL
        pattern that served the view, a versioned template name is added
        to the front of the list.

        The versioned template name is constructed by inserting the version
        before the template filename extension.

        So, if the value of the ``template_name`` attribute is
        "template_name.html" and the ``version`` keyword argument is set to
        "0.1", the return value would look like::

            ["template_name-0.1.html", "template_name.html"]
       
        """
        template_names = [self.template_name]
        version = self.kwargs.get('version', None)
        if version is not None: 
            # If a version was included in the keyword arguments, search for a
            # version-specific template first
            template_names = self.get_versioned_template_names(template_names, version)
        return template_names


class Custom404Mixin(object):
    """
    Class-based view mixin that renders a custom template in the case of
    a 404 error

    This should only be used if a custom template is required on a
    a view-by-view basis

    """
    def get_404_template_name(self):
        """
        Return the name of the template to use for 404 errors

        Defaults to `404.html`, Django's default
        """
        return '404.html'

    def dispatch(self, request, *args, **kwargs):
        try:
            return super(Custom404Mixin, self).dispatch(request, *args, **kwargs)
        except Http404:
            t = loader.get_template(self.get_404_template_name())
            return HttpResponseNotFound(t.render(RequestContext(request, {'request_path': request.path})))
