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


class FeaturedManager(models.Manager):
    """Add ability to query featured content"""
    # TODO: Make Model classes that use featured manager use
    # a QuerySet that mixes in FeaturedQuerySetMixin and have 
    # FeaturedManger.on_homepage() call through to the QuerySet's
    # on_homepage method
    def on_homepage(self):
        """Return items to be featured on homepage"""
        # While it's easy enough to just query the default manager
        # to do this, providing this convenience method abstracts
        # away the way homepage items are designated in case
        # we change the way that designation is done.
        return self.filter(on_homepage=True).filter(status__in=('published', 'staged'))
