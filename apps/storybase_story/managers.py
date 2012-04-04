"""Custom managers"""

from django.db import models

class StoryManager(models.Manager):
    """Add additional table-evel functionality to Story model"""

    def on_homepage(self):
        """Return stories to be featured on homepage"""
	# While it's easy enough to just query the default manager
	# to do this, providing this convenience method abstracts
	# away the way homepage stories are designated in case
	# we change the way that designation is done.
        return self.filter(on_homepage=True, status='published')
