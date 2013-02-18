"""
Custom QuerySet and Manager classes and mixins used across the different
StoryBase apps.
"""
from django.db import models


class FeaturedQuerySetMixin(object):
    """
    Mixin for custom QuerySet implementations for models that have
    a on_homepage flag.
    """
    def on_homepage(self):
        return self.filter(on_homepage=True)


class PublishedQuerySetMixin(object):
    """
    Mixin for custom QuerySet implementations for models that
    inherit from PublishedModel
    """
    def published(self, published_statuses=None):
        """
        Return a QuerySet of published items.
        """
        if published_statuses is None:
            # Assuming this will be a simpler, faster query
            # than using status__in=('published',) but this
            # is untested
            return self.filter(status='published')
        else:
            return self.filter(status__in=published_statuses)


class FeaturedQuerySet(FeaturedQuerySetMixin, PublishedQuerySetMixin,
        models.query.QuerySet):
    """
    QuerySet that provides utility methods for models that
    inherit from PublishedModel and have an on_homepage flag
    """
    # Implementation is in the mixins
    pass


class PublishedManagerMixin(object):
    """
    Mixin that proxies methods to its queryset that mixes in
    PublishedQuerySetMixin
    """
    def published(self, published_statuses=None):
        return self.get_query_set().published(published_statuses)


class FeaturedManager(PublishedManagerMixin, models.Manager):
    """Add ability to query featured content"""
    def get_query_set(self):
        return FeaturedQuerySet(self.model, using=self._db)

    def on_homepage(self):
        """Return items to be featured on homepage"""
        # While it's easy enough to just query the default manager
        # to do this, providing this convenience method abstracts
        # away the way homepage items are designated in case
        # we change the way that designation is done.

        # This doesn't entirely proxy the underlying queryset's
        # on_homepage method. It also filters on whether the model
        # is published
        return self.get_query_set().on_homepage()\
                   .published(published_statuses=('published', 'staged'))
