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

    def test_get_languages(self):
        from django.conf import settings
        from storybase_story.models import create_story

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
        story = create_story(title=title, summary=summary, byline=byline)
        self.assertEqual([settings.LANGUAGE_CODE], story.get_languages())

    def test_get_languages_multiple(self):
        from django.conf import settings
        from storybase_story.models import create_story, StoryTranslation

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
        story = create_story(title=title, summary=summary, byline=byline)
        translation = StoryTranslation(story=story, title="Spanish Title",
            summary="Spanish Summary", language="es")
        translation.save()
        self.assertEqual([settings.LANGUAGE_CODE, 'es'], story.get_languages())

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
