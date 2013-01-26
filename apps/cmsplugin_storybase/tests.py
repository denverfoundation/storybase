import os
from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase
from storybase.tests.base import FileCleanupMixin, PermissionTestCase
from cmsplugin_storybase.models import create_news_item
from storybase_story.models import create_story
from storybase_user.models import create_project


class NewsItemModelTest(FileCleanupMixin, TestCase):
    def setUp(self):
        super(NewsItemModelTest, self).setUp()

    def test_normalize_for_view(self):
        user = User.objects.create_user('test', 'test@example.com', 'test')
        user.first_name = "Test"
        user.last_name = "User"
        user.save()
        image_filename = "test_image.jpg"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            # Create news item
            news_item = create_news_item(title="Test News Item",
                    body="<p>This is a test news item</p>",
                    image=image,
                    image_filename=image_filename,
                    status='published',
                    on_homepage=True,
                    author=user)
            self.add_file_to_cleanup(news_item.image.file.path)
            normalized = news_item.normalize_for_view(img_width=335)
            self.assertEqual(normalized['title'], "Test News Item")
            self.assertEqual(normalized['author'], "Test U.")
            self.assertEqual(normalized['date'], news_item.created)
            self.assertIn('test_image.jpg',
                    normalized['image_html'])
            self.assertIn("This is a test news item", normalized['excerpt'])
            self.assertNotIn('url', normalized)


class TemplateTagTest(FileCleanupMixin, PermissionTestCase):
    def setUp(self):
        super(TemplateTagTest, self).setUp()

    def test_featured_items(self):
        image_filename = "test_image.jpg"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            # Create news item
            news_item = create_news_item(title="Test News Item",
                    body="<p>This is a test news item</p>",
                    image=image,
                    image_filename=image_filename,
                    status='published',
                    on_homepage=True,
                    author=self.admin_user)
            self.add_file_to_cleanup(news_item.image.file.path)
        story = create_story(title="Test Story",
                summary="Test story summary", byline="Test byline",
                status='published', author=self.user1,
                on_homepage=True)
        project = create_project(name="Test Project",
                description='Test project description',
                status='published',
                on_homepage=True)
        t = Template("{% load storybase_featured %}{% featured_items %}")
        c = Context()
        rendered = t.render(c)
        # Check that item titles are present
        self.assertIn(story.title, rendered)
        self.assertIn(news_item.title, rendered)
        self.assertIn(project.name, rendered)
        # Check ordering of items is Story, News, Project
        self.assertTrue(rendered.find(story.title) < rendered.find(news_item.title))
        self.assertTrue(rendered.find(news_item.title) < rendered.find(project.name))

    def test_featured_items_preview(self):
        image_filename = "test_image.jpg"
        app_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(app_dir, "test_files", image_filename)
        with open(img_path) as image:
            # Create a staged news item
            news_item = create_news_item(title="Test News Item",
                    body="<p>This is a test news item</p>",
                    image=image,
                    image_filename=image_filename,
                    status='staged',
                    on_homepage=True,
                    author=self.admin_user)
            self.add_file_to_cleanup(news_item.image.file.path)
        story = create_story(title="Test Story",
                summary="Test story summary", byline="Test byline",
                status='published', author=self.user1,
                on_homepage=True)
        project = create_project(name="Test Project",
                description='Test project description',
                status='published',
                on_homepage=True)
        t = Template("{% load storybase_featured %}{% featured_items %}")

        # Check that the news item isn't present for an anonymous user
        c = Context({
            'user': self.anonymous_user,
        })
        rendered = t.render(c)
        self.assertIn(story.title, rendered)
        self.assertNotIn(news_item.title, rendered)
        self.assertIn(project.name, rendered)

        # Check that the news item isn't present for a normal user 
        c = Context({
            'user': self.user1,
        })
        rendered = t.render(c)
        self.assertIn(story.title, rendered)
        self.assertNotIn(news_item.title, rendered)
        self.assertIn(project.name, rendered)

        # Check that the news item is present for an admin user
        c = Context({
            'user': self.admin_user,
        })
        rendered = t.render(c)
        self.assertIn(story.title, rendered)
        self.assertIn(news_item.title, rendered)
        self.assertIn(project.name, rendered)

        # Check that the news item is present for a super user
        c = Context({
            'user': self.superuser,
        })
        rendered = t.render(c)
        self.assertIn(story.title, rendered)
        self.assertIn(news_item.title, rendered)
        self.assertIn(project.name, rendered)


class NewsItemPermissionTest(PermissionTestCase):
    def test_user_can_view(self):
        news_item = create_news_item(title="Test News Item",
                body="<p>This is a test news item</p>",
                status='draft',
                on_homepage=True,
                author=self.user1)

        # Test author can view their own draft news item
        self.assertTrue(news_item.user_can_view(self.user1))

        # Test another user cannot view a draft news item created by
        # another user
        self.assertFalse(news_item.user_can_view(self.user2))

        # Test an admin user can view another user's draft news item
        self.assertTrue(news_item.user_can_view(self.admin_user))

        # Test that a super user can view another user's draft news _item
        self.assertTrue(news_item.user_can_view(self.superuser))

        # Publish the news item to set up for next tests
        news_item.status = 'published'
        news_item.save()
        
        # Test that author can view a published news item
        self.assertTrue(news_item.user_can_view(self.user1))

        # Test that another user can view a published news item
        self.assertTrue(news_item.user_can_view(self.user2))

    def test_anonymoususer_can_view(self):
        news_item = create_news_item(title="Test News Item",
                body="<p>This is a test news item</p>",
                status='draft',
                on_homepage=True,
                author=self.user1)

        # Anonymous user cannot view a draft
        self.assertFalse(news_item.anonymoususer_can_view(self.anonymous_user))
      
        # Anonymous user cannot view a staged item
        news_item.status = 'staged'
        news_item.save()
        self.assertFalse(news_item.anonymoususer_can_view(self.anonymous_user))

        # Anonymous user can view a published item
        news_item.status = 'published'
        news_item.save()
        self.assertTrue(news_item.anonymoususer_can_view(self.anonymous_user))


