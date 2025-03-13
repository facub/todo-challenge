# Standard imports
from datetime import datetime

# Django imports
from django.test import TestCase
from django.contrib.auth.models import AnonymousUser, User

# External imports
from rest_framework.serializers import ValidationError

# App imports
from todolist.models import Task
from todolist.serializers import TaskSerializer


class TestTaskSerializer(TestCase):
    """Test suite for the Task serializer"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="serializeruser", password="test123"
        )
        self.valid_data = {
            "title": "Valid Task",
            "description": "Valid description",
            "user": self.user.id,
            "completed": False,
            "created_at": "2021-01-01T00:00:00Z",
            "category": None,
            "priority": "medium",
            "due_date": None,
            "completed_at": "2021-01-01T00:00:00Z",
        }
        self.invalid_data = {
            "title": "",  # Empty title should fail
            "description": "",  # Empty description should fail
        }

    def test_valid_serializer(self):
        """Test valid data serialization"""
        # Create with user context
        request = self.client.post("/api/tasks/")
        request.user = self.user

        # Use context to validate user
        serializer = TaskSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], "Valid Task")

    def test_invalid_serializer(self):
        """Test invalid data rejection"""
        serializer = TaskSerializer(data=self.invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_valid_title(self):
        """Test title validation"""
        request = self.client.post("/api/tasks/")
        request.user = self.user
        serializer = TaskSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())

    def test_valid_description(self):
        """Test description validation"""
        request = self.client.post("/api/tasks/")
        request.user = self.user
        serializer = TaskSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())

    def test_to_representation_with_completed_at(self):
        """
        Test that completed_at is correctly formatted when present.
        """
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            user=self.user,
            completed_at=datetime(2021, 1, 1),
        )
        serializer = TaskSerializer(task)
        self.assertEqual(serializer.data["completed_at"], "2021-01-01 00:00:00")

    def test_to_representation_without_completed_at(self):
        """
        Test that completed_at is not present when it is None.
        """
        task = Task.objects.create(
            title="Test Task", description="Test Description", user=self.user
        )
        serializer = TaskSerializer(task)
        self.assertIsNone(serializer.data.get("completed_at"))

    def test_valid_user(self):
        """Test user validation"""
        request = self.client.post("/api/tasks/")
        request.user = self.user
        serializer = TaskSerializer(data=self.valid_data, context={"request": request})
        self.assertTrue(serializer.is_valid())

    def test_valid_serializer_authenticated(self):
        """Test valid data with authenticated user"""
        # Create authenticated request
        request = self.client.post("/api/tasks/")
        request.user = self.user

        # Initialize serializer with context
        serializer = TaskSerializer(data=self.valid_data, context={"request": request})

        # Verify validation
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["title"], "Valid Task")
        self.assertNotIn("user", serializer.validated_data)  # user is read-only

    def test_serializer_no_user(self):
        """Test validation failure for no user in request context"""
        # Create unauthenticated request
        request = self.client.post("/api/tasks/")
        request.user = AnonymousUser()

        serializer = TaskSerializer(data=self.valid_data, context={"request": request})

        # Verify error
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            str(cm.exception.detail.get("non_field_errors")[0]),
            "User authentication required",
        )

    def test_serializer_unauthenticated_user(self):
        """Test validation failure for unauthenticated user"""
        # Create unauthenticated request
        request = self.client.post("/api/tasks/")
        request.user = AnonymousUser()

        serializer = TaskSerializer(data=self.valid_data, context={"request": request})

        # Verify error
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            str(cm.exception.detail["non_field_errors"][0]),
            "User authentication required",
        )

    def test_missing_request_context(self):
        """Test error when request context is missing"""
        serializer = TaskSerializer(data=self.valid_data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            str(cm.exception.detail["non_field_errors"][0]), "Request context not found"
        )

    def test_invalid_title(self):
        """Test empty title validation"""
        request = self.client.post("/api/tasks/")
        request.user = self.user
        serializer = TaskSerializer(
            data=self.invalid_data, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_invalid_description(self):
        """Test empty description validation"""
        request = self.client.post("/api/tasks/")
        request.user = self.user
        serializer = TaskSerializer(
            data=self.invalid_data, context={"request": request}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)
