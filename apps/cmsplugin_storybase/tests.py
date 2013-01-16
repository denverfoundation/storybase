import os
from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import TestCase
from storybase.tests.base import FileCleanupMixin
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


class TemplateTagTest(FileCleanupMixin, TestCase):
    def setUp(self):
        super(TemplateTagTest, self).setUp()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
                'test@example.com', self.password)

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
                    author=self.user)
            self.add_file_to_cleanup(news_item.image.file.path)
        story = create_story(title="Test Story",
                summary="Test story summary", byline="Test byline",
                status='published', author=self.user,
                on_homepage=True)
        project = create_project(name="Test Project",
                description='Test project description',
                status='published',
                on_homepage=True)
        t = Template("{% load storybase_homepage %}{% featured_items %}")
        c = Context()
        rendered = t.render(c)
        # Check that item titles are present
        self.assertIn(story.title, rendered)
        self.assertIn(news_item.title, rendered)
        self.assertIn(project.name, rendered)
        # Check ordering of items is Story, News, Project
        self.assertTrue(rendered.find(story.title) < rendered.find(news_item.title))
        self.assertTrue(rendered.find(news_item.title) < rendered.find(project.name))
