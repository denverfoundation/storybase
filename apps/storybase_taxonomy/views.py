from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from django.http import Http404

from storybase_story.views import ExplorerRedirectView, StoryListView, StoryListWidgetView
from storybase_taxonomy.models import Category, Tag


class CategoryExplorerRedirectView(ExplorerRedirectView):
    def get_query_string(self, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            return None
        try:
            category = Category.objects.get(categorytranslation__slug=slug)
            return "topics=%d" % category.pk
        except Category.DoesNotExist:
            return None


class CategoryWidgetView(StoryListWidgetView):
    queryset = Category.objects.all()
    related_field_name = "topics"

    def get_slug_field_name(self):
        return 'categorytranslation__slug'

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs.get('slug', None)

        if slug is not None:
            queryset = queryset.filter(categorytranslation__slug=slug)
        else:
            raise AssertionError("%s must be called with a slug" %
                                 (self.__class__.__name__))

        try:
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(
                _(u"No %(verbose_name)s found matching the query") %
		       {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class TagViewMixin(object):
    queryset = Tag.objects.all()
    related_field_name = "tags"


class TagStoryListView(TagViewMixin, StoryListView):
    pass


class TagWidgetView(TagViewMixin, StoryListWidgetView):
    pass
