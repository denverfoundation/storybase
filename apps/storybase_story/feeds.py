from mimetypes import guess_type

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from storybase_asset.models import FEATURED_ASSET_THUMBNAIL_WIDTH, FEATURED_ASSET_THUMBNAIL_HEIGHT
from storybase_story.models import Story
from storybase_taxonomy.models import Category

class StoriesFeed(Feed):
    """
    Generates a feed of the 25 most recently published stories

    Allows basic filtering by topic slug by providing either a
    ``topics=SLUG`` or ``topics-exclude=SLUG`` querystring parameter to
    the GET request.

    """
    title = "%s %s" % (settings.STORYBASE_SITE_NAME, _("Stories"))
    description = _("Recent stories from ") + settings.STORYBASE_SITE_NAME

    # Map of query string parameters to Queryset filters
    QUERY_MAP = {
        'topics': 'topics__categorytranslation__slug',
    }

    def link(self):
        return reverse('explore_stories')

    def get_object(self, request, *args, **kwargs):
        # HACK: Dummy get_object implementation that doesn't actually get an
        # object, but has the side effect of storying the request object as
        # an attribute of the Feed object
        self.request = request
        return super(StoriesFeed, self).get_object(request, *args, **kwargs)

    def get_filter_kwargs(self):
        """
        Get queryset filter/exclude arguments from the request's GET parameters

        Returns a tuple of dictionaries, the first providing arguments suitable
        for a call to Queryset.filter() and the second providing arguments
        for a cal to Queryset.exclude()

        """
        filter_kwargs = {}
        exclude_kwargs = {}
        for param, lookup in self.QUERY_MAP.items():
            exclude_param = '%s-exclude' % param
            if param in self.request.GET:
                filter_kwargs[lookup] = self.request.GET[param]
            if exclude_param in self.request.GET:
                exclude_kwargs[lookup] = self.request.GET[exclude_param]
        return filter_kwargs, exclude_kwargs

    def items(self):
        # Only show non-connected, published stories in the feed
        queryset = Story.objects.exclude(source__relation_type='connected').published()
        filter_kwargs, exclude_kwargs = self.get_filter_kwargs()
        if filter_kwargs:
            queryset = queryset.filter(**filter_kwargs)
        if exclude_kwargs:
            queryset = queryset.exclude(**exclude_kwargs)
        return queryset.order_by('-published')[:25]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.summary

    def item_author_name(self, item):
        return item.contributor_name

    def item_pubdate(self, item):
        return item.published

    def item_updateddate(self, item):
        return item.last_edited

    def item_categories(self, item):
        category_objs = list(item.projects.all()) + list(item.organizations.all()) + list(item.tags.all()) + list(item.topics.all())
        return [obj.name for obj in category_objs]

    def item_copyright(self, item):
        return item.license_name()

    def item_enclosure_url(self, item):
       return item.featured_asset_thumbnail_url()

    def item_enclosure_length(self, item):
       asset = item.get_featured_asset()
       thumbnail_options = {
            'size': (FEATURED_ASSET_THUMBNAIL_WIDTH,FEATURED_ASSET_THUMBNAIL_HEIGHT),
       }
       try:
           return asset.get_thumbnail(thumbnail_options).size
       except AttributeError:
           return 0

    def item_enclosure_mime_type(self, item):
        url = item.featured_asset_thumbnail_url()
        (mtype, encoding) = guess_type(url)
        return mtype


class TopicStoriesFeed(StoriesFeed):
    """
    Generates a feed of the 25 most recently published stories in a particular
    topic

    The topic is passed to the feed via a ``slug`` keyword argument in the URL
    configuration for the feed.

    """
    def get_object(self, request, slug):
        return get_object_or_404(Category, categorytranslation__slug=slug)

    def title(self, obj):
        return "%s %s %s" % (settings.STORYBASE_SITE_NAME, obj.name, _("Stories"))

    def description(self, obj):
        return _("Recent ") + obj.name + _(" stories from ") + settings.STORYBASE_SITE_NAME

    def link(self, obj):
        return "%s?topics=%s" % (reverse('explore_stories'), obj.pk)

    def items(self, obj):
        return Story.objects.exclude(source__relation_type='connected').published().filter(topics=obj).order_by('-published')[:25]
