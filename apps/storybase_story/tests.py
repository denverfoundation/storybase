from django.test import TestCase
from storybase.utils import slugify
from models import Story, StoryTranslation

class StoryModelTest(TestCase):
    def test_auto_slug(self):
        title = 'Transportation Challenges Limit Education Choices for Denver Parents'
        story = Story()
        story.save()
        story_translation = StoryTranslation(title=title, story=story)
        self.assertEqual(story_translation.slug, '')
        story_translation.save()
        self.assertEqual(story_translation.slug, slugify(title))
