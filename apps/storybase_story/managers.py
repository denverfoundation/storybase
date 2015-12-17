from django.db import models
from storybase.managers import (FeaturedQuerySet, FeaturedManager)

class ContainerManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class SectionLayoutManager(models.Manager):
    def get_by_natural_key(self, layout_id):
        return self.get(layout_id=layout_id)


class SectionManager(models.Manager):
    """
    Custom manager that defines a natural key to make it easier to generate
    custom fixtures.

    """
    def get_by_natural_key(self, section_id):
        return self.get(section_id=section_id)


class StoryQuerySet(FeaturedQuerySet):
    """
    Custom query set to provide a high-level query interface to stories

    Based on ideas at http://dabapps.com/blog/higher-level-query-api-django-orm/

    """
    def connected(self):
        """Return stories that are connected stories"""
        return self.filter(source__relation_type='connected')

    def not_connected(self):
        """Return stories that are not connected stories"""
        return self.exclude(source__relation_type='connected')

    def seed(self):
        """Return stories that have other stories connected to them"""
        return self.not_connected()\
                 .filter(related_stories__source__relation_type='connected')\
                 .distinct()

    def template(self):
        """Return stories that are templates for other stories"""
        return self.filter(is_template=True)

    def not_template(self):
        """Return stories that are not templates for other stories"""
        return self.filter(is_template=False)

    def public(self, published_statuses=None):
        """
        Convenience method to filter for stories that are visible by all
        users
        """
        return self.published(published_statuses=published_statuses)\
                   .not_template().not_connected()


class StoryManager(FeaturedManager):
    use_for_related_fields = True

    def get_query_set(self):
        return StoryQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, story_id):
        return self.get(story_id=story_id)

    # Proxy methods to underlying querysets.
    # We could use PassThroughManager from django-model-utilities to
    # avoid this boilerplate
    def connected(self):
        return self.get_query_set().connected()

    def not_connected(self):
        return self.get_query_set().not_connected()

    def seed(self):
        return self.get_query_set().seed()

    def public(self):
        return self.get_query_set().public()


class StoryTemplateManager(models.Manager):
    def get_by_natural_key(self, template_id):
        return self.get(template_id=template_id)
