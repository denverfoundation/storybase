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

class StoryApiTest(TestCase):
    """ Test case for the internal Story API """

    def test_create_story(self):
        from storybase_story.models import create_story, Story

        title = "Transportation Challenges Limit Education Choices for Denver Parents"
        summary = """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        byline = "Mile High Connects"
        with self.assertRaises(Story.DoesNotExist):
            Story.objects.get(storytranslation__title=title)
        story = create_story(title=title, summary=summary, byline=byline)
        self.assertEqual(story.title, title)
        self.assertEqual(story.summary, summary)
        self.assertEqual(story.byline, byline)
        retrieved_story = Story.objects.get(pk=story.pk)
        self.assertEqual(retrieved_story.title, title)
        self.assertEqual(retrieved_story.summary, summary)
        self.assertEqual(retrieved_story.byline, byline)
