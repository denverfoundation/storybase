from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.views.generic import DetailView
from django.utils.translation import ugettext as _

from storybase_user.models import Organization, Project

class ModelIdDetailView(DetailView):
    """DetailView that retrieves objects by custom id instead of pk"""

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

class OrganizationDetailView(ModelIdDetailView):

    context_object_name = "organization"
    queryset = Organization.objects.all()


class ProjectDetailView(ModelIdDetailView):

    context_object_name = "project"
    queryset = Project.objects.all()
