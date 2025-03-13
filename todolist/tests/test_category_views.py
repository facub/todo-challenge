# Django imports
from django.test import TestCase
from django.contrib.auth.models import User

# External imports
from rest_framework import status
from rest_framework.test import APIClient

# App imports
from todolist.models import TaskCategory


class TestTaskCategoryView(TestCase):
    """Test suite for the TaskCategory model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="categoryuser", password="pass123"
        )
        self.client = APIClient()
        self.category = TaskCategory.objects.create(name="Work")

    def test_category_creation(self):
        """Test that created categories are associated with the authenticated user"""
        self.client.force_authenticate(user=self.user)
        data = {"name": "New Category"}
        response = self.client.post("/api/categories/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category = TaskCategory.objects.get(id=response.data["id"])
        self.assertEqual(category.name, "New Category")

    def test_custom_delete_category(self):
        """Test custom delete action for categories"""
        self.client.force_authenticate(user=self.user)
        category = TaskCategory.objects.create(name="To Delete")
        url = f"/api/categories/{category.id}/delete/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TaskCategory.objects.filter(id=category.id).exists())

    def test_get_all_categories(self):
        """Test fetching all categories"""
        self.client.force_authenticate(user=self.user)
        TaskCategory.objects.create(name="Personal")
        response = self.client.get("/api/categories/all/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Work")
        self.assertEqual(response.data[1]["name"], "Personal")
