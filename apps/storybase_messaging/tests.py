"""Tests for the actions app"""

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.template.loader import TemplateDoesNotExist
from django.test import TestCase
from django.utils.translation import activate, get_language

from storybase.tests.base import SloppyComparisonTestMixin
from storybase_user.models import ADMIN_GROUP_NAME
from storybase_messaging.managers import StoryNotificationQuerySet
from storybase_messaging.models import SiteContactMessage, StoryNotification
from storybase_story.models import create_story

class EmailSendingTestCaseMixin(object):
    def check_backend(self): 
        backend = getattr(settings, 'EMAIL_BACKEND', None)
        if backend != 'django.core.mail.backends.locmem.EmailBackend':
            self.fail("You must use the in-memory e-mail backend when "
                      "running this test")

    def get_sent_emails(self):
        from django.core.mail import outbox
        return outbox

    def get_sent_email(self, index):
        return self.get_sent_emails()[index]

    def assertInSentSubjects(self, s):
        for email in self.get_sent_emails():
            if s in email.subject:
                return True

        self.fail('"%s" not found in sent email subjects' % (s))


class SiteContactMessageModelTest(EmailSendingTestCaseMixin, TestCase):
    """Test methods of the SiteContactMessge model"""
    def test_email_sent_on_save(self):
        """
        Tests that an email is sent when a message is saved. 
        """
        self.check_backend()

        name = 'Jane Doe'
        email = 'jane@doe.com'
        phone = '123-456-7890'
        message_body = ("I am interested in your site.\n"
                        "Please give me more information\n"
                        "\n"
                        "Thanks,\n"
                        "Jane")
        admin_group = Group.objects.create(name=ADMIN_GROUP_NAME)
        admin = User.objects.create(username='admin', 
            password='password', email='admin@example.com')
        admin.groups.add(admin_group)
        admin.save()
        SiteContactMessage.objects.create(name=name, email=email,
            phone=phone, message=message_body)
            
        sent_email = self.get_sent_email(0) 
        self.assertEqual(sent_email.from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(sent_email.subject, 
                         "New message from %s" % email)
        self.assertIn(admin.email, sent_email.to)
        self.assertIn(name, sent_email.body)
        self.assertIn(phone, sent_email.body)
        self.assertIn(message_body, sent_email.body)


class StoryNotificationModelTest(TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@floodlightproject.org', self.password)
        # Save the environment language as some of the tests switch to
        # a specific language
        self.current_language = get_language()

    def tearDown(self):
        # Switch to the language that was detected when we started
        activate(self.current_language)

    def test_get_language_choices(self):
        """Test retrieving languages for message templates"""
        expected_language = "en-us"
        expected_languages = [expected_language]
        if settings.LANGUAGE_CODE != expected_language:
            expected_languages.append(settings.LANGUAGE_CODE)
        story = create_story(title="Test Story", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        activate(expected_language)
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        self.assertEqual(notification.get_language_choices(), expected_languages)

    def test_get_body_template(self):
        """Test loading body template for a specific story notification message"""
        story = create_story(title="Test Story", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        try:
            notification.get_body_template("text")
        except TemplateDoesNotExist:
            self.fail("Template not returned")

    def test_get_subject_template(self):
        """Test loading subject template for a specific story notification message"""
        story = create_story(title="Test Story", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        try:
            notification.get_subject_template()
        except TemplateDoesNotExist:
            self.fail("Template not returned")

    def test_get_context(self):
        story1 = create_story(title="test story 1", summary="test summary",
                                  byline="test byline", status='draft',
                                  author=self.user)
        story2 = create_story(title="test story 2", summary="test summary",
                                  byline="test byline", status='draft',
                                  author=self.user)
        story3 = create_story(title="test story 3", summary="test summary",
                                  byline="test byline", status='published',
                                  author=self.user)
        notification = StoryNotification.objects.get(story=story2, notification_type='unpublished')
        # StoryNotification._common_context is cached per-thread. Clobber
        # it so we get fresh values
        StoryNotification._common_context = None
        context = notification.get_context()
        self.assertEqual(context['story'], story2)
        self.assertIn(story1, context['unpublished_stories'])
        self.assertIn(story3, context['recent_stories'])

    def test_get_subject(self):
        story = create_story(title="Test Story", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        # The template text is likely to change, so to make the tests
        # flexible, check for the key elements instead of matching entire strings
        # For the unpublished notification, make sure the subject is nonempty
        self.assertNotEqual(notification.get_subject(), "")
        story.status = 'published'
        story.save()
        notification = StoryNotification.objects.get(story=story, notification_type='published')
        # For the published notification, make sure the story title is in the subject
        self.assertIn(story.title, notification.get_subject())

    def test_get_text_content(self):
        story = create_story(title="Test Story", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        # The template text is likely to change, so to make the tests
        # flexible, just check that the content is nonempty 
        content = notification.get_text_content()
        self.assertNotEqual(content, "")
        story.status = 'published'
        story.save()
        notification = StoryNotification.objects.get(story=story, notification_type='published')
        content = notification.get_text_content()
        self.assertNotEqual(content, "")


class StoryNotificationQuerySetTest(TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@floodlightproject.org', self.password)

    def test_emails(self):
        story1 = create_story(title="Test Story 1", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story2 = create_story(title="Test Story 2", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story3 = create_story(title="Test Story 3", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        qs = StoryNotificationQuerySet(model=StoryNotification)
        emails = qs.order_by('story__created').emails()
        self.assertEqual(len(emails), 3)
        self.assertIn(story1.title, emails[1].body)

    def test_ready_to_send(self):
        story1 = create_story(title="Test Story 1", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story2 = create_story(title="Test Story 2", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story3 = create_story(title="Test Story 3", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        notification1 = StoryNotification.objects.get(story=story1)
        notification2 = StoryNotification.objects.get(story=story2)
        notification3 = StoryNotification.objects.get(story=story3)
        send_on = notification2.send_on
        ready_qs = StoryNotificationQuerySet(model=StoryNotification).ready_to_send(send_on)
        self.assertEqual(ready_qs.count(), 2)
        self.assertIn(notification1, ready_qs)
        self.assertIn(notification2, ready_qs)
        ready_qs = StoryNotificationQuerySet(model=StoryNotification).ready_to_send()
        self.assertEqual(ready_qs.count(), 0)


class StoryNotificationManagerTest(EmailSendingTestCaseMixin, TestCase):
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@floodlightproject.org', self.password)

    def test_send_emails(self):
        self.check_backend()

        story1 = create_story(title="Test Story 1", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story2 = create_story(title="Test Story 2", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story3 = create_story(title="Test Story 3", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)
        story1.status = 'published'
        story2.status = 'published'
        story1.save()
        story2.save()
        # At this point there should be two "unpublished" notifications ready
        # to be sent.
        StoryNotification.objects.send_emails()
        self.assertEqual(len(self.get_sent_emails()), 2)
        self.assertInSentSubjects(story1.title)
        self.assertInSentSubjects(story2.title)
        # Now there should be no notifications ready to send
        self.assertEqual(StoryNotification.objects.all().ready_to_send().count(), 0)
        # The notification items we sent should have their ``sent``
        # timestamp set
        self.assertNotEqual(StoryNotification.objects.get(
            story=story1, notification_type='published').sent,
            None)
        self.assertNotEqual(StoryNotification.objects.get(
            story=story2, notification_type='published').sent,
            None)


class StoryNotificationSignalsTest(SloppyComparisonTestMixin, TestCase):
    """
    Test that StoryNotification signal handlers are properly wired to Story 
    model save signals
    """
    def setUp(self):
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 'test@floodlightproject.org', self.password)
        
    def test_unpublished_notification_created(self):
        """Test that a notification model instance is created when a story is saved"""
        story = create_story(title="Test Story", summary="Test Summary",
                                  byline="Test Byline", status='draft',
                                  author=self.user)

        five_days = timedelta(days=5)
        send_on = datetime.now() + five_days 
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        self.assertEqual(notification.sent, None)
        self.assertTimesEqualish(notification.send_on, send_on)

    def test_unpublished_notification_send_on_updated(self):
        """Test that the send_on date is updated when a story is re-saved"""
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status='draft',
                             author=self.user)
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        original_send_on = notification.send_on
        story.save()
        notification = StoryNotification.objects.get(story=story, notification_type='unpublished')
        self.assertTrue(original_send_on < notification.send_on)

    def test_unpublished_notification_deleted_on_publish(self):
        """
        Test that any unsent notification is deleted when the story is 
        published
        """
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status='draft',
                             author=self.user)
        story.status = 'published'
        story.save()
        self.assertEqual(StoryNotification.objects.filter(story=story, notification_type='unpublished').count(), 0)

    def test_published_notification_created(self):
        """
        Test that a published notification is created when a story
        is published
        """
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status='draft',
                             author=self.user)
        self.assertEqual(StoryNotification.objects.filter(story=story, notification_type='published').count(), 0)
        story.status = 'published'
        story.save()
        self.assertEqual(StoryNotification.objects.filter(story=story, notification_type='published').count(), 1)

    def test_communication_preferences_honored(self):
        """
        Test that a user's communication preferences are honored and
        a notification is not created if a user turns them off
        """
        profile = self.user.userprofile
        profile.notify_story_unpublished = False
        profile.notify_story_published = False
        profile.save()
        story = create_story(title="Test Story", summary="Test Summary",
                             byline="Test Byline", status='draft',
                             author=self.user)
        self.assertEqual(StoryNotification.objects.count(), 0)
        story.status = 'published'
        story.save()
        self.assertEqual(StoryNotification.objects.count(), 0)
