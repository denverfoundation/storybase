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
        self.tag_attrs = [
            { 'name': 'Schools' },
            { 'name': 'Housing' },
            { 'name': 'education' },
            { 'name': 'neighborhood' },
            { 'name': 'food' },
        ]

    def test_get_list(self):
        for attrs in self.tag_attrs:
            Tag.objects.create(**attrs)
        self.assertEqual(Tag.objects.count(), len(self.tag_attrs))
        uri = '/api/0.1/tags/'
        resp = self.api_client.get(uri, format='json')
        self.assertValidJSONResponse(resp)
        self.assertEqual(Tag.objects.count(),
                         len(self.deserialize(resp)['objects']))
        retrieved_tag_names = [tag['name'] for tag
                               in self.deserialize(resp)['objects']]
        for attrs in self.tag_attrs:
            self.assertIn(attrs['name'], retrieved_tag_names)


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
        self.assertEqual(created_obj.tag_id, returned_id)
        # Compare the created model instance with the post data
        self.assertEqual(created_obj.name, post_data['name'])
        # Test that the created object is associated with the story
        self.assertEqual(self.story.tags.count(), 1)
        self.assertIn(created_obj, self.story.tags.all())

    def test_post_list_with_story_existing(self):
        for attrs in self.tag_attrs:
            Tag.objects.create(**attrs)
        tag = Tag.objects.all()[0]
        post_data = {
            'tag_id': tag.tag_id
        }
        self.assertEqual(Tag.objects.count(), len(self.tag_attrs))
        self.assertEqual(self.story.tags.count(), 0)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/tags/stories/%s/' % (self.story.story_id)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        resp = self.api_client.post(uri, format='json', data=post_data)
        self.assertHttpCreated(resp)
        returned_id = resp['location'].split('/')[-2]
        # Confirm that the number of tags is unchanged
        self.assertEqual(Tag.objects.count(), len(self.tag_attrs))
        # Confirm that a tag was added to the story
        self.assertEqual(self.story.tags.count(), 1)
        # Confirm the values match
        self.assertEqual(tag.tag_id, self.deserialize(resp)['tag_id'])
        self.assertEqual(tag.name, self.deserialize(resp)['name'])
        story_tag = self.story.tags.get()
        self.assertEqual(story_tag, tag)

    def test_delete_detail_with_story(self):
        for attrs in self.tag_attrs:
            Tag.objects.create(**attrs)
        tag = Tag.objects.all()[0]
        self.story.tags.add(tag)
        self.story.save()
        self.assertEqual(Tag.objects.count(), len(self.tag_attrs))
        self.assertEqual(self.story.tags.count(), 1)
        self.api_client.client.login(username=self.username,
                                     password=self.password)
        uri = '/api/0.1/tags/%s/stories/%s/' % (tag.tag_id, self.story.story_id)
        resp = self.api_client.delete(uri)
        self.assertHttpAccepted(resp)
        self.assertEqual(Tag.objects.count(), len(self.tag_attrs))
        self.assertEqual(self.story.tags.count(), 0)
