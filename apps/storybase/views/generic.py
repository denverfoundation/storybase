""""Common generic views"""
try:
    import shortuuid
except ImportError:
    shortuuid

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.utils.translation import get_language, ugettext as _

from storybase.utils import simple_language_changer

class ModelIdDetailView(DetailView):
    """DetailView that retrieves objects by custom id instead of pk"""
    @method_decorator(simple_language_changer)
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
        module_name = queryset.model._meta.module_name
        return '%s_id' % module_name

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
