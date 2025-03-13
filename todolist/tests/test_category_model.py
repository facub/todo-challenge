# Django imports
from django.test import TestCase

# App imports
from todolist.models import TaskCategory


class TestTaskCategoryModel(TestCase):
    """Test suite for the TaskCategory model"""

    def setUp(self):
        self.category = TaskCategory.objects.create(name="Work")

    def test_category_creation(self):
        """Test category creation"""
        self.assertEqual(self.category.name, "Work")

    def test_category_str_representation(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), "Work")
