from django.db import models

from storybase.managers import FeaturedManager


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


class StoryManager(FeaturedManager):
    def get_by_natural_key(self, story_id):
        return self.get(story_id=story_id)


class StoryTemplateManager(models.Manager):
    def get_by_natural_key(self, template_id):
        return self.get(template_id=template_id)
