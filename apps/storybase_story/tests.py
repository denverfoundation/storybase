"""Unit tests for storybase_story app"""

from time import sleep
from django.conf import settings
from django.test import TestCase
from storybase.tests import SloppyTimeTestCase
from storybase.utils import slugify
from storybase_asset.models import HtmlAsset, HtmlAssetTranslation
from models import (create_story, Story, StoryTranslation, 
    create_section, Section, SectionAsset)

class StoryModelTest(SloppyTimeTestCase):
    """Unit tests for Story Model"""

    def test_auto_slug(self):
        """Test slug field is set automatically"""
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
        story = Story()
        story.save()
        story_translation = StoryTranslation(title=title, story=story)
        self.assertEqual(story_translation.slug, '')
        story_translation.save()
        self.assertEqual(story_translation.slug, slugify(title))

    def test_get_languages(self):
        """Test Story.get_languages() method for a single translation"""
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        """Test Story.get_languages() for multiple translations"""
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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

    def test_auto_set_published_on_create(self):
        """
        Test that the published date gets set on object creation when the
        status is set to published
        """
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
        summary = """
            Many families in the Denver metro area use public
            transportation instead of a school bus because for them, a
            quality education is worth hours of daily commuting. Colorado's
            school choice program is meant to foster educational equity,
            but the families who benefit most are those who have time and
            money to travel. Low-income families are often left in a lurch.
            """
        byline = "Mile High Connects"
        story = create_story(title=title, summary=summary, byline=byline,
                             status='published')
        self.assertNowish(story.published)

    def test_auto_set_published_on_status_change(self):
        """
        Test that the published date gets set when the status is changed
        to published
        """ 
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        # Default status should be draft 
        self.assertEqual(story.status, 'draft')
        # and there should be no published date
        self.assertEqual(story.published, None)
        story.status = 'published'
        story.save()
        self.assertNowish(story.published)


class StoryApiTest(TestCase):
    """Test case for the internal Story API"""

    def test_create_story(self):
        """Test create_story() creates a Story instance"""
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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

class StoryManagerTest(TestCase):
    """Test case for custom manager for Story model"""

    def has_story_title(self, title, stories):
	"""
	Utility method to check that a given title is in a queryset of stories
	"""
	for story in stories:
	       break
	else:
	    self.fail("Story with title '%s' not found" % title)

    def test_on_homepage(self):
        """
	Test that StoryManager.on_homepage() returns filtered queryset
	"""
	homepage_titles = (
	    "The Power of Play: Playground Locations in the Children's Corridor",
	    "Birth Trends in the Children's Corridor: Focus on Foreign-born Mothers",
	    "Shattered Dreams: Revitalizing Hope in Original Aurora",
	    "A School Fight Rallies Hinkley High School Mothers to Organize",
	    "Transportation Challenges Limit Education Choices for Denver Parents")
	other_titles = ("Story 1", "Story 2")
	for title in homepage_titles + other_titles:
	    on_homepage = title in homepage_titles
	    create_story(title=title, on_homepage=on_homepage,
			 status='published')
	homepage_stories = Story.objects.on_homepage()
	self.assertEqual(homepage_stories.count(), len(homepage_titles))
	for title in homepage_titles:
	    self.has_story_title(title, homepage_stories)

    def test_on_homepage_published_only(self):
	"""
	Test that StoryManager.on_homepage() returns only published stories
	"""
	published_titles = (
	    "The Power of Play: Playground Locations in the Children's Corridor",
	    "Birth Trends in the Children's Corridor: Focus on Foreign-born Mothers")
	unpublished_titles = (
	    "Shattered Dreams: Revitalizing Hope in Original Aurora",
	    "A School Fight Rallies Hinkley High School Mothers to Organize",
	    "Transportation Challenges Limit Education Choices for Denver Parents")
	for title in published_titles + unpublished_titles:
	    status = 'draft'
	    if title in published_titles:
		status = 'published'
	    create_story(title=title, on_homepage=True, status=status)
			 
	homepage_stories = Story.objects.on_homepage()
	self.assertEqual(homepage_stories.count(), len(published_titles))
	for title in published_titles:
	    self.has_story_title(title, homepage_stories)

class ViewsTest(TestCase):
    """Tests for story-related views"""

    def test_homepage_story_list(self):
	"""Test homepage_story_list()"""
	import lxml.html
	from storybase_story.views import homepage_story_list

	homepage_titles = (
	    "The Power of Play: Playground Locations in the Children's Corridor",
	    "Birth Trends in the Children's Corridor: Focus on Foreign-born Mothers",
	    "Shattered Dreams: Revitalizing Hope in Original Aurora",
	    "A School Fight Rallies Hinkley High School Mothers to Organize",
	    "Transportation Challenges Limit Education Choices for Denver Parents")
	for title in homepage_titles:
	    create_story(title=title, on_homepage=True,
			 status='published')
	    # Force different timestamps for stories
	    sleep(1)
	homepage_stories = Story.objects.on_homepage()
        html = homepage_story_list()
	fragment = lxml.html.fromstring(html)
	# TODO: Finish implementing this
	elements = fragment.cssselect('li')
	self.assertEqual(len(elements), homepage_stories.count())
	sorted_titles = tuple(reversed(homepage_titles))
	for i in range(sorted_titles):
	   self.assertTrue(sorted_titles[i] in elements[i].text_content())


class SectionModelTest(SloppyTimeTestCase):
    """Test Case for Section model"""

    def test_update_story_timestamp(self):
        """
        Test that a section's story's last edited timestamp is updated when
        the section is saved
        """
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        section = create_section(title="Test Section 1", story=story)
        sleep(2)
        section.save()
        self.assertNowish(story.last_edited)

class SectionApiTest(TestCase):
    """Test case for public Section creation API"""

    def test_create_section(self):
        """Test that create_section() function creates a new Section"""
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        section_title = "Test Section 1"
        with self.assertRaises(Section.DoesNotExist):
            Section.objects.get(sectiontranslation__title=section_title)
        section = create_section(title=section_title, story=story)
        self.assertEqual(section.title, section_title)
        self.assertEqual(section.story, story)
        retrieved_section = Section.objects.get(pk=section.pk)
        self.assertEqual(retrieved_section.title, section_title)
        self.assertEqual(retrieved_section.story, story)

class SectionAssetModelTest(TestCase):
    """Test Case for Asset to Section relation through model"""

    def test_auto_add_assets_to_story(self):
        """
        Test that when an asset is added to a section it is also added
        to the Story
        """
        # Create a story
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        # Confirm that the story has no assets
        self.assertEqual(story.assets.count(), 0)
        # create a Section
        section = create_section(title="Test Section 1", story=story)
        # create a HtmlAsset
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(title='Test Asset', asset=asset)
        translation.save()
        # Assign the asset to the section
        section_asset = SectionAsset(section=section, asset=asset, weight=0)
        section_asset.save()
        # Confirm the asset is in the section's list
        self.assertTrue(asset in section.assets.select_subclasses())
        # Confirm that the asset is in the story's list
        self.assertTrue(asset in story.assets.select_subclasses())

    def test_already_added_asset(self):
        """
        Test that when an asset that is related to a story is also
        related to a section, nothing breaks
        """
        # Create a story
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        # create a HtmlAsset
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(title='Test Asset', asset=asset)
        translation.save()
        # assign the asset to the story
        story.assets.add(asset)
        story.save()
        # confirm the asset is added to the story
        self.assertTrue(asset in story.assets.select_subclasses())
        # create a Section
        section = create_section(title="Test Section 1", story=story)
        # Assign the asset to the section
        section_asset = SectionAsset(section=section, asset=asset, weight=0)
        section_asset.save()
        # Confirm the asset is in the section's list
        self.assertTrue(asset in section.assets.select_subclasses())
        # Confirm that the asset is in the story's list
        self.assertTrue(asset in story.assets.select_subclasses())

    def test_remove_asset(self):
        """
        Test that when an asset is removed from a section, it is not 
        removed from the story
        """
        # Create a story
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
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
        # Confirm that the story has no assets
        self.assertEqual(story.assets.count(), 0)
        # create a Section
        section = create_section(title="Test Section 1", story=story)
        # create a HtmlAsset
        asset = HtmlAsset()
        asset.save()
        translation = HtmlAssetTranslation(title='Test Asset', asset=asset)
        translation.save()
        # Assign the asset to the section
        section_asset = SectionAsset(section=section, asset=asset, weight=0)
        section_asset.save()
        # Confirm the asset is in the section's list
        self.assertTrue(asset in section.assets.select_subclasses())
        # Confirm that the asset is in the story's list
        self.assertTrue(asset in story.assets.select_subclasses())
        # Delete the asset from the section.
        section_asset.delete()
        # Confirm that the asset is NOT in the section's list
        self.assertFalse(asset in section.assets.select_subclasses())
        # Confirm that the asset is in the story's list
        self.assertTrue(asset in story.assets.select_subclasses())
