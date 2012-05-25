"""Tests for taxonomy app"""
from django.test import TestCase

from storybase_taxonomy.models import (Category, CategoryTranslation,
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
