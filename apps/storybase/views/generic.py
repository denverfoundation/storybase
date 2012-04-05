""""Common generic views"""

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import DetailView
from django.utils.translation import get_language, ugettext as _

class ModelIdDetailView(DetailView):
    """DetailView that retrieves objects by custom id instead of pk"""

    def render_to_response(self, context, **response_kwargs):
	"""Handle language-aware paths"""
        language_code = get_language()
	obj = context.get(self.context_object_name)
        available_languages = obj.get_languages()
        if language_code not in available_languages:
            alt_lang = settings.LANGUAGE_CODE
            if alt_lang not in available_languages:
                alt_lang = available_languages[0]
            path = obj.get_absolute_url()
            return redirect('/%s%s' % (alt_lang, path))
        
        return super(ModelIdDetailView, self).render_to_response(
	    context, **response_kwargs)

    def get_object(self):
	"""Retrieve the object by it's model specific id instead of pk"""
	queryset = self.get_queryset()
        module_name = queryset.model._meta.module_name
	obj_id_name = '%s_id' % module_name
	obj_id = self.kwargs.get(obj_id_name, None)
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
	    raise Http404(_(u"No %(verbose_name)s found matching the query") %
		            {'verbose_name': queryset.model._meta.verbose_name})
        return obj
