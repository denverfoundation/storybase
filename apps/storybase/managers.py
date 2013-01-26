from django.db import models

class FeaturedManager(models.Manager):
    """Add ability to query featured content"""

    def on_homepage(self):
        """Return items to be featured on homepage"""
        # While it's easy enough to just query the default manager
        # to do this, providing this convenience method abstracts
        # away the way homepage items are designated in case
        # we change the way that designation is done.
        return self.filter(on_homepage=True).filter(status__in=('published', 'staged'))
