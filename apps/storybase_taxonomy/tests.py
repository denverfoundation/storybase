"""Tests for taxonomy app"""
from django.contrib.auth.models import User 
from django.test import TestCase

from tastypie.test import ResourceTestCase, TestApiClient

from storybase_story.models import create_story
from storybase_taxonomy.models import (Category, CategoryTranslation, Tag,
                                       create_category)

class CategoryModelTest(TestCase):
    """Test the Category model"""

    def test_auto_slug(self):
        """Test slug field is set automatically"""
        category = Category.objects.create()
        translation = CategoryTranslation.objects.create(
            name="Charter Schools", category=category)
        self.assertEqual(category.slug, "charter-schools")


class CategoryApiTest(TestCase):
    """Test case for the internal Category API"""

    def test_create_category(self):
        name = "Education"
        slug = "education"
        category = create_category(name=name)
        self.assertEqual(category.name, name)
        self.assertEqual(category.slug, slug)


class TagResourceTest(ResourceTestCase):
    def setUp(self):
        super(TagResourceTest, self).setUp()
        self.username = 'test'
        self.password = 'test'
        self.user = User.objects.create_user(self.username, 
            'test@example.com', self.password)
        self.user2 = User.objects.create_user("test2", "test2@example.com",
                                              "test2")
        self.story = create_story(title="Test Story", summary="Test Summary",
            byline="Test Byline", status="published", language="en", 
            author=self.user)

    def test_post_list_with_story(self):
        post_data = {
            'name': 'Schools'
        }
        self.assertEqual(Tag.objects.count(), 0)
        self.assertEqual(self.story.tags.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/tags/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        returned_id = resp['location'].split('/')[-2]
        # Confirm that a location object was created
        self.assertEqual(Tag.objects.count(), 1)
        # Compare the response data with the post_data
        self.assertEqual(self.deserialize(resp)['name'],
                         post_data['name'])
        created_obj = Tag.objects.get()
        # Compare the id from the resource URI with the created object
        self.assertEqual(created_obj.location_id, returned_id)
        # Compare the created model instance with the post data
        self.assertEqual(created_obj.name, post_data['name'])
        # Test that the created object is associated with the story
        self.assertEqual(self.story.tags.count(), 1)
        self.assertIn(created_obj, self.story.tags.all())
