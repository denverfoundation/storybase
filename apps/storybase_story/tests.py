"""Unit tests for storybase_story app"""

from time import sleep

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.test import TestCase
from django.utils import simplejson

from tastypie.test import ResourceTestCase

from storybase.tests.base import SloppyComparisonTestMixin
from storybase.utils import slugify
from storybase_asset.models import HtmlAsset, HtmlAssetTranslation
from storybase_geo.models import Location
from storybase_story.api import StoryResource
from storybase_story.forms import SectionRelationAdminForm
from storybase_story.models import (create_story, Story, StoryTranslation, 
    create_section, Section, SectionAsset, SectionRelation)


class SectionRelationFormTest(TestCase):
    """Test custom forms for SectionRelations"""

    def test_select_label(self):
	"""
	Test that both Section title and its Story title appear in select
	labels
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
        section1 = create_section(title="Test Section 1", story=story)
        section2 = create_section(title="Test Section 2", story=story)
        form = SectionRelationAdminForm()
        choices_list = list(form.fields['parent'].widget.choices)
        self.assertIn(story.title, choices_list[1][1])
        self.assertIn(story.title, choices_list[2][1])


class StoryModelTest(TestCase, SloppyComparisonTestMixin):
    """Unit tests for Story Model"""

    def test_auto_slug(self):
        """Test slug field is set automatically"""
        title = ('Transportation Challenges Limit Education Choices for '
                 'Denver Parents')
        story = Story()
        story.save()
        story_translation = StoryTranslation(title=title, story=story)
        story_translation.save()
        self.assertEqual(story.slug, slugify(title))

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
        story_languages = story.get_languages()
        self.assertEqual(len(story_languages), 2)
        for code in (settings.LANGUAGE_CODE, 'es'):
            self.assertIn(code, story_languages)

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

    def test_contributor_name(self):
        """
        Test that the Story.contributor_name returns the first name
        and last initial of the Story's author user
        """
        user = User.objects.create(username='admin', first_name='Jordan',
                                   last_name='Wirfs-Brock')
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
                             author=user)
        self.assertEqual(story.contributor_name, 'Jordan W.')


    def test_contributor_name_no_last_name(self):
        """
        Test that the Story.contributor_name returns the first name
        of the Story's author user when no last name is set
        """
        user = User.objects.create(username='admin', first_name='Jordan')
                                   
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
                             author=user)
        self.assertEqual(story.contributor_name, 'Jordan')

    def test_contributor_name_no_names(self):
        """
        Test that the Story.contributor_name returns an empty string 
         when there is no first or last name
        """
        user = User.objects.create(username='admin')
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
                             author=user)
        self.assertEqual(story.contributor_name, '')


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
	Test that Story.objects.on_homepage() returns filtered queryset
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
	Test that story.objects.on_homepage() returns only published stories
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
        html = homepage_story_list(len(homepage_titles))
	fragment = lxml.html.fromstring(html)
	# TODO: Finish implementing this
	elements = fragment.cssselect('.stories > li')
	self.assertEqual(len(elements), homepage_stories.count())
	sorted_titles = tuple(reversed(homepage_titles))
	for i in range(len(sorted_titles)):
	   self.assertTrue(sorted_titles[i] in elements[i].text_content())


class SectionModelTest(TestCase, SloppyComparisonTestMixin):
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


class StructureTest(TestCase):
    """Test rendering of different story structures"""

    def test_linear_toc_simple(self):
        """
        Test that a table of contents can be rendered for a
        simple story structure
        """
        import lxml.html

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
        section_data = [
            {'title': 'Children and Affordable Housing', 'weight': 0},
            {'title': 'School Quality', 'weight': 1},
            {'title': 'Early Childhood Education', 'weight': 2},
            {'title': 'Low-Income Families and FRL', 'weight': 3},
            {'title': 'Transportation Spending', 'weight': 4},
            {'title': 'The Choice System', 'weight': 5}
        ]
        story = create_story(title=title, structure='linear',
                             summary=summary, byline=byline)
        for section_dict in section_data:
            create_section(title=section_dict['title'],
                           story=story,
                           weight=section_dict['weight'],
                           root=True)
        rendered_toc = story.structure.render_toc(format='html')
        #print rendered_toc
        fragment = lxml.html.fromstring(rendered_toc)
        elements = fragment.cssselect('li')
        self.assertEqual(len(elements), len(section_data) + 1)
	self.assertEqual(elements[0].text_content().strip(), "Summary")
        for i in range(1, len(section_data)):
            self.assertEqual(section_data[i-1]['title'],
                             elements[i].text_content().strip())
        
    def test_sections_flat_linear_nested(self):
        """
        Test sections_flat() when sections are arranged in a linear
        fashion with one root and each subsequent section nested below
        the previous
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        SectionRelation.objects.create(parent=section1, child=section2)
        SectionRelation.objects.create(parent=section2, child=section3)
        SectionRelation.objects.create(parent=section3, child=section4)
        self.assertEqual(story.structure.sections_flat, [section1, section2, 
                                                section3, section4])

    def test_sections_flat_spider(self):
        """
        Test sections_flat() when sections are arranged as children of a
        single root section.
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        SectionRelation.objects.create(parent=section1, child=section2,
                                       weight=0)
        SectionRelation.objects.create(parent=section1, child=section3,
                                       weight=1)
        SectionRelation.objects.create(parent=section1, child=section4,
                                       weight=2)
        self.assertEqual(story.structure.sections_flat, [section1, section2,
                                                 section3, section4])

    def test_sections_flat_tree(self):
        """
        Test sections_flat() when sections are arranged in a tree-like
        structure
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        section5 = create_section(title="Last section", story=story)
        SectionRelation.objects.create(parent=section1, child=section2,
                                       weight=0)
        SectionRelation.objects.create(parent=section2, child=section3,
                                       weight=0)
        SectionRelation.objects.create(parent=section2, child=section4,
                                       weight=1)
        SectionRelation.objects.create(parent=section1, child=section5,
                                       weight=1)
        self.assertEqual(story.structure.sections_flat, [section1, section2,
                                                 section3, section4,
                                                 section5])

    def test_sections_flat_no_sections(self):
        """
        Test sections_flat() when there are no child sections
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        self.assertEqual(story.structure.sections_flat, [])

    def test_sections_flat_one_section(self):
        """
        Test sections_flat() when there is only a single root section
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        self.assertEqual(story.structure.sections_flat, [section1])

    def test_sections_flat_no_root_section(self):
        """
        Test sections_flat() when there is only a single root section
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=False)
        self.assertEqual(story.structure.sections_flat, [])

    def test_get_next_section_linear_nested(self):
        """
        Test get_next_section() when sections are arranged in a linear
        fashion with one root and each subsequent section nested below
        the previous
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        SectionRelation.objects.create(parent=section1, child=section2)
        SectionRelation.objects.create(parent=section2, child=section3)
        SectionRelation.objects.create(parent=section3, child=section4)
        self.assertEqual(story.structure.get_next_section(section1),   
                         section2)
        self.assertEqual(story.structure.get_next_section(section2),
                         section3)
        self.assertEqual(story.structure.get_next_section(section3),
                         section4)
        self.assertEqual(story.structure.get_next_section(section4),
                         None)

    def test_get_previous_section_linear_nested(self):
        """
        Test get_previous_section() when sections are arranged in a linear
        fashion with one root and each subsequent section nested below
        the previous
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        SectionRelation.objects.create(parent=section1, child=section2)
        SectionRelation.objects.create(parent=section2, child=section3)
        SectionRelation.objects.create(parent=section3, child=section4)
        self.assertEqual(story.structure.get_previous_section(section1),   
                         None)
        self.assertEqual(story.structure.get_previous_section(section2),
                         section1)
        self.assertEqual(story.structure.get_previous_section(section3),
                         section2)
        self.assertEqual(story.structure.get_previous_section(section4),
                         section3)

    def test_get_next_section_spider(self):
        """
        Test test_get_next_section() when sections are arranged as children
        of a single root section.
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        SectionRelation.objects.create(parent=section1, child=section2,
                                       weight=0)
        SectionRelation.objects.create(parent=section1, child=section3,
                                       weight=1)
        SectionRelation.objects.create(parent=section1, child=section4,
                                       weight=2)
        self.assertEqual(story.structure.get_next_section(section1),   
                         section2)
        self.assertEqual(story.structure.get_next_section(section2),
                         section3)
        self.assertEqual(story.structure.get_next_section(section3),
                         section4)
        self.assertEqual(story.structure.get_next_section(section4),
                         None)

    def test_get_previous_section_spider(self):
        """
        Test test_get_previous_section() when sections are arranged as 
        children of a single root section.
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        SectionRelation.objects.create(parent=section1, child=section2,
                                       weight=0)
        SectionRelation.objects.create(parent=section1, child=section3,
                                       weight=1)
        SectionRelation.objects.create(parent=section1, child=section4,
                                       weight=2)
        self.assertEqual(story.structure.get_previous_section(section1),   
                         None)
        self.assertEqual(story.structure.get_previous_section(section2),
                         section1)
        self.assertEqual(story.structure.get_previous_section(section3),
                         section2)
        self.assertEqual(story.structure.get_previous_section(section4),
                         section3)

    def test_get_next_section_tree(self):
        """
        Test get_next_section() when sections are arranged in a tree-like
        structure
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        section5 = create_section(title="Last section", story=story)
        SectionRelation.objects.create(parent=section1, child=section2,
                                       weight=0)
        SectionRelation.objects.create(parent=section2, child=section3,
                                       weight=0)
        SectionRelation.objects.create(parent=section2, child=section4,
                                       weight=1)
        SectionRelation.objects.create(parent=section1, child=section5,
                                       weight=1)
        self.assertEqual(story.structure.get_next_section(section1),   
                         section2)
        self.assertEqual(story.structure.get_next_section(section2),   
                         section3)
        self.assertEqual(story.structure.get_next_section(section3),   
                         section4)
        self.assertEqual(story.structure.get_next_section(section4),   
                         section5)
        self.assertEqual(story.structure.get_next_section(section5),   
                         None)

    def test_get_previous_section_tree(self):
        """
        Test get_previous_section() when sections are arranged in a tree-like
        structure
        """
        title = ("Neighborhood Outreach for I-70 Alignment Impacting "
                 "Elyria, Globeville and Swansea")
        summary = """
            The City of Denver and Colorado Department of Transportation 
            (CDOT) are working together to do neighborhood outreach
            regarding the I-70 alignment between Brighton Boulevard and
            Colorado. For detailed information on the neighborhood outreach
            efforts please visit www.DenverGov.org/ccdI70.
            """
        byline = "Denver Public Works and CDOT"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section(title="Background and context",
                                  story=story,
                                  root=True)
        section2 = create_section(title="Decisions to be made", story=story)
        section3 = create_section(title="Who has been involved", 
                                  story=story)
        section4 = create_section(title="Next steps", story=story)
        section5 = create_section(title="Last section", story=story)
        SectionRelation.objects.create(parent=section1, child=section2,
                                       weight=0)
        SectionRelation.objects.create(parent=section2, child=section3,
                                       weight=0)
        SectionRelation.objects.create(parent=section2, child=section4,
                                       weight=1)
        SectionRelation.objects.create(parent=section1, child=section5,
                                       weight=1)
        self.assertEqual(story.structure.get_previous_section(section1),   
                         None)
        self.assertEqual(story.structure.get_previous_section(section2),   
                         section1)
        self.assertEqual(story.structure.get_previous_section(section3),   
                         section2)
        self.assertEqual(story.structure.get_previous_section(section4),   
                         section3)
        self.assertEqual(story.structure.get_previous_section(section5),   
                         section4)

    def _get_section(self, sections, section_id):
	"""
	Utility to get a section with a given ID from a list of simplified
	section dictionaries
	"""
        for section in sections:
	    if section['section_id'] == section_id:
	        return section

    def test_sections_json_spider_three_levels(self):
	"""
	Test that sections_json() returns the sections in the correct 
	order and with the correct relationships
	"""

        title = ("Taking Action for the Social and Emotional Health of "
	         "Young Children: A Report to the Community from the Denver "
		 "Early Childhood Council")
	summary = ("Now, Denver has a plan of action to make it easier for "
	           "families to access early childhood mental health "
		   "information, intervention and services.")
	byline = "Denver Early Childhood Council"
        story = create_story(title=title, summary=summary, byline=byline)
        section1 = create_section("We're ready to take action. Are you?",
			          story=story, weight=7)
	section2 = create_section("Ricardo's Story",
			          story=story, weight=2)
	section3 = create_section("Meeting the need for better child mental health services",
			           story=story, root=True, weight=1)
	section4 = create_section("Healthy Minds Support Strong Futures",
			          story=story, weight=5) 
	section5 = create_section("Community Voices",
			          story=story, weight=3)
	section6 = create_section("Our Vision: That All Children in Denver are Valued, Healthy and Thriving",
			          story=story, weight=4)
	section7 = create_section("Defining a \"Framework for Change\" with Actionable Goals and Strategies",
			          story=story, weight=5) 
        section8 = create_section("How Can the Plan Make a Difference?",
			          story=story, weight=5)
	section9 = create_section("Impact", story=story, weight=6)
        SectionRelation.objects.create(parent=section6, child=section8,
                                       weight=0)
        SectionRelation.objects.create(parent=section7, child=section9,
                                       weight=0)
        SectionRelation.objects.create(parent=section6, child=section7,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section1,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section6,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section4,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section5,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section2,
                                       weight=0)
	json_sections = simplejson.loads(story.structure.sections_json(
		include_summary=False, include_call_to_action=False))
	self.assertIn(
	  section8.section_id,
	  self._get_section(json_sections, section6.section_id)['children'])
	self.assertIn(
	  section9.section_id,
	  self._get_section(json_sections, section7.section_id)['children'])
	self.assertIn(
	  section7.section_id,
	  self._get_section(json_sections, section6.section_id)['children'])
	self.assertIn(
	  section1.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section6.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section4.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section5.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section2.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])

    def test_sections_json_spider_three_levels_with_summary_and_call(self):
	"""
	Test that sections_json() returns the sections in the correct 
	order and with the correct relationships and also includes
	the summary and call to action
	"""
        title = ("Taking Action for the Social and Emotional Health of "
	         "Young Children: A Report to the Community from the Denver "
		 "Early Childhood Council")
	summary = ("Now, Denver has a plan of action to make it easier for "
	           "families to access early childhood mental health "
		   "information, intervention and services.")
	call_to_action = ("Test call to action.")
	byline = "Denver Early Childhood Council"
        story = create_story(title=title, summary=summary, byline=byline,
			     call_to_action=call_to_action)
        section1 = create_section("We're ready to take action. Are you?",
			          story=story, weight=7)
	section2 = create_section("Ricardo's Story",
			          story=story, weight=2)
	section3 = create_section("Meeting the need for better child mental health services",
			           story=story, root=True, weight=1)
	section4 = create_section("Healthy Minds Support Strong Futures",
			          story=story, weight=5) 
	section5 = create_section("Community Voices",
			          story=story, weight=3)
	section6 = create_section("Our Vision: That All Children in Denver are Valued, Healthy and Thriving",
			          story=story, weight=4)
	section7 = create_section("Defining a \"Framework for Change\" with Actionable Goals and Strategies",
			          story=story, weight=5) 
        section8 = create_section("How Can the Plan Make a Difference?",
			          story=story, weight=5)
	section9 = create_section("Impact", story=story, weight=6)
        SectionRelation.objects.create(parent=section6, child=section8,
                                       weight=0)
        SectionRelation.objects.create(parent=section7, child=section9,
                                       weight=0)
        SectionRelation.objects.create(parent=section6, child=section7,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section1,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section6,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section4,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section5,
                                       weight=0)
        SectionRelation.objects.create(parent=section3, child=section2,
                                       weight=0)
	json_sections = simplejson.loads(story.structure.sections_json(
		include_summary=True, include_call_to_action=True))
	self.assertIn(
	  section8.section_id,
	  self._get_section(json_sections, section6.section_id)['children'])
	self.assertIn(
	  section9.section_id,
	  self._get_section(json_sections, section7.section_id)['children'])
	self.assertIn(
	  section7.section_id,
	  self._get_section(json_sections, section6.section_id)['children'])
	self.assertIn(
	  section1.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section6.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section4.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section5.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertIn(
	  section2.section_id,
	  self._get_section(json_sections, section3.section_id)['children'])
	self.assertEqual(json_sections[0]['section_id'], 'summary')
	self.assertEqual(json_sections[0]['next_section_id'], 
			 json_sections[1]['section_id'])
	self.assertEqual(json_sections[1]['previous_section_id'], 'summary')
	self.assertEqual(json_sections[-1]['section_id'], 'call-to-action')
	self.assertEqual(json_sections[-1]['previous_section_id'], 
			 json_sections[-2]['section_id'])
	self.assertEqual(json_sections[-2]['next_section_id'], 'call-to-action')


class StoryResourceTest(ResourceTestCase):
    """Tests for backend to Tastypie-driven REST endpoint"""
    def setUp(self):
        super(StoryResourceTest, self).setUp()
        self.resource = StoryResource()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@example.com', self.password)

    def assertPointInList(self, point, l):
        for p in l:
            if p == point:
                return True
        else:
            self.fail("Point (%f, %f) not found in %s" % (point[0], point[1], str(l)))

    def test_locations_in_points(self):
        """
        Test that related Location coordinates are included in the ``points``
        field of a story's serialized data
        """
        locations = [
            Location.objects.create(name="The Piton Foundation", lat=39.7438167, lng=-104.9884953),
            Location.objects.create(name="Hull House", lat=41.8716782, lng=-87.6474517)
        ]
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status='published')
        story.locations.add(locations[0])
        story.locations.add(locations[1])
        story.save()
        req = HttpRequest()
        req.GET['story_id'] = story.story_id
        resp = self.resource.get_detail(req)
        dehydrated = simplejson.loads(resp.content)
        self.assertEqual(len(dehydrated['points']), 2)
        for location in locations:
            self.assertPointInList([location.lat, location.lng],
                                   dehydrated['points'])

    def test_post_list_unauthorized(self):
        """Test that a user cannot create a story if they aren't logged in"""
        return self.assertHttpUnauthorized(self.api_client.post('/api/0.1/stories/', format='json'))

    def test_post_list(self):
        """Test that a user can create a story"""
        post_data = {
            'title': "Test Story",
            'summary': "Test Summary",
            'byline': "Test Byline",
            'status': "draft",
            'language': "en",
        }
        self.assertEqual(Story.objects.count(), 0)
        self.api_client.client.login(username=self.username, password=self.password)
        response = self.api_client.post('/api/0.1/stories/',
                               format='json', data=post_data)
        self.assertHttpCreated(response)
        self.assertEqual(Story.objects.count(), 1)
        created_story = Story.objects.get()
        self.assertEqual(created_story.title, post_data['title'])
        self.assertEqual(created_story.summary, post_data['summary'])
        self.assertEqual(created_story.byline, post_data['byline'])
        self.assertEqual(created_story.status, post_data['status'])
        self.assertEqual(created_story.get_languages(), [post_data['language']])
        self.assertEqual(created_story.author, self.user)
        # Check that the story id is returned by the endpoint
        returned_story_id = response['location'].split('/')[-2]
        self.assertEqual(created_story.story_id, returned_story_id)

    def test_post_list_es(self):
        """Test that a user can create a story in Spanish"""
        post_data = {
            'title': "Test Story",
            'summary': "Test Summary",
            'byline': "Test Byline",
            'status': "draft",
            'language': "es",
        }
        self.assertEqual(Story.objects.count(), 0)
        self.api_client.client.login(username=self.username, password=self.password)
        response = self.api_client.post('/api/0.1/stories/',
                               format='json', data=post_data)
        self.assertHttpCreated(response)
        self.assertEqual(Story.objects.count(), 1)
        created_story = Story.objects.get()
        self.assertEqual(created_story.title, post_data['title'])
        self.assertEqual(created_story.summary, post_data['summary'])
        self.assertEqual(created_story.byline, post_data['byline'])
        self.assertEqual(created_story.status, post_data['status'])
        self.assertEqual(created_story.get_languages(), [post_data['language']])
        self.assertEqual(created_story.author, self.user)
        # Check that the story id is returned by the endpoint
        returned_story_id = response['location'].split('/')[-2]
        self.assertEqual(created_story.story_id, returned_story_id)



class StoryExploreResourceTest(TestCase):
    """Test story exploration REST endpoint"""

    def setUp(self):
        self.resource = StoryResource()

    def _rebuild_index(self):
        """Call management command to rebuild the Haystack search index"""
        from django.core.management import call_command
        call_command('rebuild_index', interactive=False, verbosity=0)

    def test_distance_query(self):
        """
        Test that resource can be filtered based on distance about a point
        """
        locations = [
            Location.objects.create(name="The Piton Foundation", lat=39.7438167, lng=-104.9884953),
            Location.objects.create(name="Hull House", lat=41.8716782, lng=-87.6474517)
        ]
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status='published')
        story.locations.add(locations[0])
        story.save()
        story2 = create_story(title="Test Story 2", summary="Test Summary 2",
                             byline="Test Byline 2", status='published')
        story2.locations.add(locations[1])
        story2.save()
        # TODO: Figure out why this is neccessary
        self._rebuild_index()
        req = HttpRequest()
        req.method = 'GET'
        req.GET['near'] = '39.7414581054089@-104.9877892025,1'
        resp = self.resource.explore_get_list(req)
        dehydrated = simplejson.loads(resp.content)
        self.assertEqual(len(dehydrated['objects']), 1)
        self.assertEqual(dehydrated['objects'][0]['story_id'], story.story_id)
