# Standard imports
from datetime import datetime

# Django imports
from django.test import TestCase
from django.contrib.auth.models import User

# App imports
from todolist.models import Task


class TestTaskModel(TestCase):
    """Test suite for the Task model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.task = Task.objects.create(
            title="Test Task", description="Test Description", user=self.user
        )

    def test_task_creation(self):
        """Test task creation and default values"""
        self.assertEqual(self.task.completed, False)
        self.assertIsInstance(self.task.created_at, datetime)
        self.assertEqual(str(self.task), "Test Task (Pending)")

    def test_task_str_representation(self):
        """Test __str__ method output"""
        self.task.completed = True
        self.assertEqual(str(self.task), "Test Task (Completed)")
