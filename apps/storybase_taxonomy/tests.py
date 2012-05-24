"""Tests for taxonomy app"""
from django.test import TestCase

from storybase_taxonomy.models import Category, CategoryTranslation

class CategoryModelTest(TestCase):
    """Test the Category model"""

    def test_auto_slug(self):
        """Test slug field is set automatically"""
        category = Category.objects.create()
        translation = CategoryTranslation.objects.create(
            name="Charter Schools", category=category)
        self.assertEqual(category.slug, "charter-schools")
