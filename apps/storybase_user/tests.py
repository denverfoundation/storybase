"""Unit tests for users app"""

from time import sleep

from django.contrib.auth.models import Group, User
from django.core import urlresolvers
from django.test import TestCase
from django.test.client import Client
from django.utils import translation

from storybase.utils import slugify
from storybase_story.models import create_story
from storybase_user.auth.forms import ChangeUsernameEmailForm
from storybase_user.models import (create_organization, create_project,
    Organization, OrganizationStory, OrganizationTranslation,
    Project, ProjectStory, ProjectTranslation,
    ADMIN_GROUP_NAME)
from storybase_user.utils import is_admin, get_admin_emails

class ChangeUsernameEmailFormTest(TestCase):
    """Tests for the change username/email form"""
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)
        self.user2 = User.objects.create_user('test3',
            'test3@example.com', 'test3')
        # Valid form data.  Delete/alter keys in this
        self.form_data = {
            'password': self.password,
            'new_email1': 'test2@example.com',
            'new_email2': 'test2@example.com',
        }

    def test_password_required(self):
        data = {
            'password': '',
            'new_email1': 'test2@example.com',
            'new_email2': 'test2@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form._errors)

    def test_new_email1_required(self):
        data = {
            'password': 'test',
            'new_email1': '',
            'new_email2': 'test2@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_email1', form._errors)

    def test_new_email2_required(self):
        data = {
            'password': 'test',
            'new_email1': 'test2@example.com',
            'new_email2': '',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_email2', form._errors)

    def test_emails_must_match(self):
        data = {
            'password': 'test',
            'new_email1': 'test2@example.com',
            'new_email2': 'testwrong@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_email2', form._errors)

    def test_new_email_already_used(self):
        """
        Test that the new email is not already associated with a user
        """
        data = {
            'password': 'test',
            'new_email1': 'test3@example.com',
            'new_email2': 'test3@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_email2', form._errors)

    def test_incorrect_password(self):
        """
        Test that the form is invalid if the password field doesn't match
        the user's password.
        """
        data = {
            'password': 'testwrong',
            'new_email1': 'test2@example.com',
            'new_email2': 'test2@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form._errors)

    def test_form_valid(self):
        data = {
            'password': 'test',
            'new_email1': 'test2@example.com',
            'new_email2': 'test2@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertTrue(form.is_valid())

    def test_save(self):
        """
        Test that the user object is updated when the form is saved.
        """
        data = {
            'password': 'test',
            'new_email1': 'test2@example.com',
            'new_email2': 'test2@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertTrue(form.is_valid())
        form.save()
        user = User.objects.get(pk=self.user.pk)
        self.assertEqual(user.email, data['new_email1'])
        self.assertEqual(user.username, data['new_email1'])

    def test_original_email_saved(self):
        """
        Test that the original email is saved in an attribute of the 
        form after the form is saved.
        """
        old_email = self.user.email
        data = {
            'password': 'test',
            'new_email1': 'test2@example.com',
            'new_email2': 'test2@example.com',
        }
        form = ChangeUsernameEmailForm(self.user, data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(form.previous_data['email'], old_email)


class OrganizationModelTest(TestCase):
    def _create_organization(self, name, language):
        org = Organization()
        org.save()
        trans = OrganizationTranslation(name=name, language=language,
            organization=org)
        trans.save()
        return org

    def test_get_translated_field(self):
        """
        Tests that you can get a translated field as if it were the model's own
        """
        org_name_en = "Mile High Connects"
        org = self._create_organization(org_name_en, "en")
        self.assertEqual(org.name, org_name_en)

    def test_get_translated_field_default_fallback(self):
        """
        Tests that if a translated field doesn't exist in the current
        language, it falls back to the default language.
        """
        org_name_en = "Mile High Connects"
        org = self._create_organization(org_name_en, "en")
        translation.activate('es')
        self.assertEqual(org.name, org_name_en)

    def test_get_translated_field_first_fallback(self):
        """
        Tests that if a translated field doesn't exist in the current
        language, and it doesn't exist in the default language, the 
        first available language is used
        """
        org_name_es = "Mile High Conecta"
        org = self._create_organization(org_name_es, 'es')
        translation.activate('en')
        self.assertEqual(org.name, org_name_es)

    def test_auto_slug(self):
        name = 'Mile High Connects'
        organization = Organization()
        organization.save()
        organization_translation = OrganizationTranslation(name=name, organization=organization)
        organization_translation.save()
        self.assertEqual(organization.slug, slugify(name))

    def test_auto_unique_slug(self):
        name = 'Mile High Connects'
        organization = create_organization(name=name)
        self.assertEqual(organization.slug, "mile-high-connects")
        organization2 = create_organization(name=name)
        self.assertEqual(organization2.slug, "mile-high-connects-2")
        self.assertEqual(Organization.objects.filter(
            slug="mile-high-connects").count(), 1)

    def test_add_story(self):
        organization = create_organization(name='Mile High Connects')
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
        weight = 15
        organization.add_story(story, weight) 
        self.assertTrue(story in organization.curated_stories.all())
        OrganizationStory.objects.get(organization=organization, story=story,
                                 weight=weight)

    def test_ordered_stories_by_time(self):
        """ Tests that ordered_stories will order by date if weights are equal """
        organization = create_organization(name='Mile High Connects')
        story1 = create_story(title='Story 1', summary='', byline='')
        story2 = create_story(title='Story 2', summary='', byline='')
        organization.add_story(story1, 0)
        sleep(2)
        organization.add_story(story2, 0)
        stories = organization.ordered_stories()
        self.assertEqual(stories.count(), 2)
        self.assertEqual(stories[0], story2)
        self.assertEqual(stories[1], story1)

    def test_ordered_stories_by_weight(self):
        """ Tests that ordered_stories will order first by weight """
        organization = create_organization(name='Mile High Connects')
        story1 = create_story(title='Story 1', summary='', byline='')
        story2 = create_story(title='Story 2', summary='', byline='')
        organization.add_story(story1, 5)
        sleep(2)
        organization.add_story(story2, 25)
        stories = organization.ordered_stories()
        self.assertEqual(stories.count(), 2)
        self.assertEqual(stories[0], story1)
        self.assertEqual(stories[1], story2)

class OrganizationApiTest(TestCase):
    def test_create_organization(self):

        name = "Mile High Connects"
        website_url = "http://www.urbanlandc.org/collaboratives/mile-high-connects/"
        description = 'Mile High Connects (formerly know as the Mile High Transit Opportunity Collaborative) is an emerging collaborative of nonprofit and philanthropic organizations working together to ensure the creation of the region\'s $6.7 billion FasTracks transit system benefits all communities in the region, including low-income populations.'
        with self.assertRaises(Organization.DoesNotExist):
            Organization.objects.get(organizationtranslation__name=name)
        org = create_organization(name=name, description=description, website_url=website_url)
        self.assertEqual(org.name, name)
        self.assertEqual(org.description, description)
        self.assertEqual(org.website_url, website_url)
        retrieved_org = Organization.objects.get(pk=org.pk)
        self.assertEqual(retrieved_org.name, name)
        self.assertEqual(retrieved_org.description, description)
        self.assertEqual(retrieved_org.website_url, website_url)

class ProjectModelTest(TestCase):
    def test_auto_slug(self):
        name = 'The Metro Denver Regional Equity Atlas'
        project = Project()
        project.save()
        project_translation = ProjectTranslation(name=name, project=project)
        project_translation.save()
        self.assertEqual(project.slug, slugify(name))

    def test_auto_unique_slug(self):
        name = "The Metro Denver Regional Equity Atlas"
        description = """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region\'s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region\'s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region\'s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        project = create_project(name=name, description=description)
        self.assertEqual(project.slug,
                         "the-metro-denver-regional-equity-atlas")
        project2 = create_project(name=name, description=description)
        self.assertEqual(project2.slug,
                         "the-metro-denver-regional-equity-atlas-2")
        self.assertEqual(Project.objects.filter(
            slug="the-metro-denver-regional-equity-atlas").count(), 1)

    def test_add_story(self):
        name = "The Metro Denver Regional Equity Atlas"
        description = """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region\'s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region\'s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region\'s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        project = create_project(name=name, description=description)
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
        weight = 15
        project.add_story(story, weight) 
        self.assertTrue(story in project.curated_stories.all())
        ProjectStory.objects.get(project=project, story=story,
                                 weight=weight)

    def test_ordered_stories_by_time(self):
        """ Tests that ordered_stories will order by date if weights are equal """
        name = "The Metro Denver Regional Equity Atlas"
        description = """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region\'s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region\'s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region\'s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        project = create_project(name=name, description=description)
        story1 = create_story(title='Story 1', summary='', byline='')
        story2 = create_story(title='Story 2', summary='', byline='')
        project.add_story(story1, 0)
        sleep(2)
        project.add_story(story2, 0)
        stories = project.ordered_stories()
        self.assertEqual(stories.count(), 2)
        self.assertEqual(stories[0], story2)
        self.assertEqual(stories[1], story1)

    def test_ordered_stories_by_weight(self):
        """ Tests that ordered_stories will order first by weight """
        name = "The Metro Denver Regional Equity Atlas"
        description = """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region\'s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region\'s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region\'s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        project = create_project(name=name, description=description)
        story1 = create_story(title='Story 1', summary='', byline='')
        story2 = create_story(title='Story 2', summary='', byline='')
        project.add_story(story1, 5)
        sleep(2)
        project.add_story(story2, 25)
        stories = project.ordered_stories()
        self.assertEqual(stories.count(), 2)
        self.assertEqual(stories[0], story1)
        self.assertEqual(stories[1], story2)

class ProjectApiTest(TestCase):
    def test_create_project(self):
        name = "The Metro Denver Regional Equity Atlas"
        description = """
            The Denver Regional Equity Atlas is a product of Mile High
            Connects (MHC), which came together in 2011 to ensure that 
            the region\'s significant investment in new rail and bus
            service will provide greater access to opportunity and a
            higher quality of life for all of the region\'s residents, but
            especially for economically disadvantaged populations who
            would benefit the most from safe, convenient transit service.

            The Atlas visually documents the Metro Denver region\'s
            demographic, educational, employment, health and housing
            characteristics in relation to transit, with the goal of
            identifying areas of opportunity as well as challenges to
            creating and preserving quality communities near transit.
            """
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(projecttranslation__name=name)
        project = create_project(name=name, description=description)
        self.assertEqual(project.name, name)
        self.assertEqual(project.description, description)
        retrieved_project = Project.objects.get(pk=project.pk)
        self.assertEqual(retrieved_project.name, name)
        self.assertEqual(retrieved_project.description, description)


class UtilityTest(TestCase):
    """Test for utility functions"""
    def setUp(self):
        self.admin_group = Group.objects.create(name=ADMIN_GROUP_NAME)
    def test_get_admin_emails(self):
        """Test get_admin_emails() returns a list of administrator emails"""
        admin1 = User.objects.create(username='admin1', password='password',
                                     email='foo@bar.com')
        admin1.groups.add(self.admin_group)
        admin1.save()
        admin2 = User.objects.create(username='admin2', password='password',
                                     email='foo2@bar.com')
        admin2.groups.add(self.admin_group)
        admin2.save()
        nonadmin = User.objects.create(username='test1', 
                                       password='password',
                                       email='foo3@bar.com')
        admin_emails = get_admin_emails()
        self.assertEqual(len(admin_emails), 2)
        self.assertIn(admin1.email, admin_emails)
        self.assertIn(admin2.email, admin_emails)

    def test_get_admin_emails_fallback(self):
        """
        Tests that superuser emails are defined if there are no users in
        the admin group
        """
        admin1 = User.objects.create(username='admin1', password='password',
                                     email='foo@bar.com',
                                     is_superuser=True)
        admin2 = User.objects.create(username='admin2', password='password',
                                     email='foo2@bar.com',
                                     is_superuser=True)
        nonadmin = User.objects.create(username='test1', 
                                       password='password',
                                       email='foo3@bar.com')
        admin_emails = get_admin_emails()
        self.assertEqual(len(admin_emails), 2)
        self.assertIn(admin1.email, admin_emails)
        self.assertIn(admin2.email, admin_emails)

    def test_is_admin(self):
        admin = User.objects.create_user(username='admin1', password='password',
                                         email='foo@bar.com')
        superuser = User.objects.create_user(username='superuser1',
                                             password='superuser1',
                                             email='superuser1@example.com')
        nonadmin = User.objects.create_user(username='test1', 
                                       password='password',
                                       email='foo3@bar.com')
        admin.groups.add(self.admin_group)
        admin.save()
        superuser.is_superuser = True
        superuser.save()

        self.assertTrue(is_admin(admin))
        self.assertTrue(is_admin(superuser))
        self.assertFalse(is_admin(nonadmin))


class AccountStoriesViewTest(TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)
        self.path = "/accounts/stories/"
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_no_publish_button_for_never_published(self):
        """
        Test that no publish button shows up when a story has never been
        published.
        """
        story = create_story(title='Story 1', summary='', byline='',
                author=self.user)
        publish_url = urlresolvers.reverse('story_publish', kwargs={
            'slug': story.slug }) 
        unpublish_url = urlresolvers.reverse('story_unpublish', kwargs={
            'slug': story.slug }) 
        resp = self.client.get(self.path)
        self.assertNotIn(unpublish_url, resp.content)
        self.assertNotIn(publish_url, resp.content)

    def test_publish_button_for_once_published(self):
        """
        Test that a publish button appears when a story was published
        at one time, but is now unpublished.
        """
        story = create_story(title='Story 1', summary='', byline='',
                author=self.user)
        story.status = 'published'
        story.save()
        story.status = 'draft'
        story.save()
        publish_url = urlresolvers.reverse('story_publish', kwargs={
            'slug': story.slug }) 
        unpublish_url = urlresolvers.reverse('story_unpublish', kwargs={
            'slug': story.slug }) 
        resp = self.client.get(self.path)
        self.assertNotIn(unpublish_url, resp.content)
        self.assertIn(publish_url, resp.content)

    def test_unpublished_button_for_published(self):
        """
        Test that an unpublish button is available for published stories
        """
        story = create_story(title='Story 1', summary='', byline='',
                author=self.user)
        story.status = 'published'
        story.save()
        publish_url = urlresolvers.reverse('story_publish', kwargs={
            'slug': story.slug }) 
        unpublish_url = urlresolvers.reverse('story_unpublish', kwargs={
            'slug': story.slug }) 
        resp = self.client.get(self.path)
        self.assertNotIn(publish_url, resp.content)
        self.assertIn(unpublish_url, resp.content)
