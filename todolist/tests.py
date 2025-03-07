# Standard imports
from datetime import datetime
# Django imports
from django.test import TestCase
from django.contrib.auth.models import User
# External imports
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
# App imports
from .models import Task
from .serializers import TaskSerializer


class TestTaskModelTests(TestCase):
    """Test suite for the Task model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            user=self.user
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

class TestTaskSerializerTests(TestCase):
    """Test suite for the Task serializer"""

    def setUp(self):
        self.user = User.objects.create_user(username="serializeruser", password="test123")
        self.valid_data = {
            "title": "Valid Task",
            "description": "Valid description",
            "user": self.user.id
        }
        self.invalid_data = {
            "title": "",  # Empty title should fail
            "description": "Invalid task"
        }

    def test_valid_serializer(self):
        """Test valid data serialization"""
        serializer = TaskSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        task = serializer.save()
        self.assertEqual(task.title, "Valid Task")
        self.assertEqual(task.description, "Valid description")
        self.assertEqual(task.user, self.user)

    def test_invalid_serializer(self):
        """Test invalid data rejection"""
        serializer = TaskSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

class TestAuthTests(APITestCase):
    """Test authentication flow"""

    def test_user_registration(self):
        """Test user registration endpoint"""
        data = {"username": "newuser", "password": "newpass123"}
        response = self.client.post("/api/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", response.data)
        self.assertEqual(User.objects.count(), 1)

    def test_token_authentication(self):
        """Test JWT token acquisition"""
        user = User.objects.create_user(username="testuser", password="testpass123")
        response = self.client.post("/api/token/", {
            "username": "testuser",
            "password": "testpass123"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

class TestTaskAPITests(APITestCase):
    """Test Task API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(username="apiuser", password="apipass123")
        self.task = Task.objects.create(
            title="Existing Task",
            user=self.user
        )
        self.client = APIClient()

    def test_create_task_authenticated(self):
        """Test task creation by authenticated user"""
        self.client.force_authenticate(user=self.user)
        data = {"title": "New Task", "description": "New description", "user": self.user.id}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.data.get("title"), "New Task")
        self.assertEqual(response.data.get("description"), "New description")

    def test_create_task_unauthenticated(self):
        """Test task creation without authentication"""
        data = {"title": "Should Fail"}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_tasks(self):
        """Test listing user's tasks"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("count"), 1)

    def test_toggle_complete(self):
        """Test toggle completion status"""
        self.client.force_authenticate(user=self.user)
        url = f"/api/tasks/{self.task.id}/toggle-complete/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    def test_filter_tasks(self):
        """Test filtering tasks by completion status"""
        Task.objects.create(title="Completed Task", completed=True, user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/tasks/?completed=True")
        self.assertEqual(response.data.get("count"), 1)
        self.assertTrue(response.data.get("results")[0]["completed"])

    def test_search_tasks(self):
        """Test search by title/description"""
        Task.objects.create(title="Shopping List", description="Groceries", user=self.user)
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/tasks/?search=shopping")
        self.assertEqual(response.data.get("count"), 1)
        self.assertEqual(response.data.get("results")[0]["title"], "Shopping List")
        self.assertEqual(response.data.get("results")[0]["description"], "Groceries")
