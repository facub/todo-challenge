# Standard imports
from datetime import datetime, timedelta
from unittest.mock import patch

# Django imports
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from django.contrib.auth.models import AnonymousUser

# External imports
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.serializers import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

# App imports
from .models import Task
from .serializers import TaskSerializer


class TestTaskModelTests(TestCase):
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


class TestTaskSerializerTests(TestCase):
    """Test suite for the Task serializer"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="serializeruser", password="test123"
        )
        self.valid_data = {
            "title": "Valid Task",
            "description": "Valid description",
            "user": self.user.id,
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


class TestAuthTests(APITestCase):
    """Test suite for authentication endpoints"""

    def setUp(self):
        # Create a test user and client
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.client = APIClient()
        self.url_register = reverse("user-registration")
        self.url_login = reverse("user-login")
        self.url_logout = reverse("user-logout")

    def test_user_registration(self):
        """Test successful user registration"""
        # Send registration request with valid data
        data = {"username": "newuser", "password": "newpass123"}
        response = self.client.post("/api/register/", data)

        # Verify response and database state
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_missing_fields(self):
        """Test registration with missing required fields"""
        # Send empty data to registration endpoint
        response = self.client.post(self.url_register, {})

        # Verify error response for missing fields
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
        self.assertIn("password", response.data)

    def test_login_success(self):
        """Test successful user authentication"""
        # Send valid credentials
        data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(self.url_login, data)

        # Verify response structure and status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Test login with incorrect password"""
        data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(self.url_login, data)

        # Verify error response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"], "Invalid credentials")

    def test_login_missing_username(self):
        """Test login request without username"""
        data = {"password": "testpass123"}
        response = self.client.post(self.url_login, data)

        # Verify error handling
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"], "Invalid credentials")

    def test_login_missing_password(self):
        """Test login request without password"""
        data = {"username": "testuser"}
        response = self.client.post(self.url_login, data)

        # Verify error handling
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error"], "Invalid credentials")

    def test_user_logout(self):
        """Test logout with valid refresh token"""
        # Generate a refresh token for the user
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh_token": str(refresh)}

        # Send logout request
        response = self.client.post(self.url_logout, data)

        # Verify token is blacklisted
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        with self.assertRaises(Exception):
            RefreshToken(str(refresh)).verify()  # Token should be invalid

    def test_logout_without_token(self):
        """Test logout attempt without providing refresh token"""
        # Send empty data to logout endpoint
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_logout, {"refresh_token": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_get_method(self):
        """Test GET method is not allowed for logout endpoint"""
        self.client.force_authenticate(user=self.user)
        refresh_token = RefreshToken.for_user(self.user)
        response = self.client.get(
            self.url_logout, {"refresh_token": str(refresh_token)}
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_logout_invalid_token(self):
        """Test logout attempt with invalid refresh token"""
        # Send invalid token to logout endpoint
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_logout, {"refresh_token": "invalid-token"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("rest_framework_simplejwt.tokens.RefreshToken")
    def test_logout_with_exception(self, mock_refresh_token):
        """Test logout with an exception being raised"""
        # Mock RefreshToken to raise a TokenError
        mock_refresh_token.side_effect = TokenError("Token is invalid or expired")

        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # Attempt to logout
        response = self.client.post(self.url_logout, {"refresh_token": "some-token"})

        # Verify response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid or expired token")

    @patch("rest_framework_simplejwt.tokens.RefreshToken.blacklist")
    def test_logout_general_exception(self, mock_blacklist):
        """
        Test logout with unexpected server error during token invalidation
        """
        # Mock blacklist method to raise an exception
        mock_blacklist.side_effect = Exception("Simulated database failure")

        # User authentication and token generation
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        data = {"refresh_token": str(refresh)}

        # Execute logout request
        response = self.client.post(self.url_logout, data)

        # Verify response and error message
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "Server error during logout")


class TestCheckAuthAPI(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )
        self.url = reverse("check-auth")  # Get URL from name

    def test_authenticated_user(self):
        """Verify response for authenticated user"""
        # Generate valid access token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        # Make request
        response = self.client.get(self.url)

        # Validate response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["authenticated"])
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertIsNotNone(response.data["token_expires"])

    def test_unauthenticated_request(self):
        """Verify 401 response for unauthenticated users"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_expired_token(self):
        """Verify 401 response with expired token"""
        # Create expired token
        token = AccessToken.for_user(self.user)
        token.set_exp(lifetime=-timedelta(days=1))  # Expired 1 day ago

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token(self):
        """Verify 401 response with invalid token"""
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_missing_token(self):
        """Verify 401 response with missing token"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestTaskAPITests(APITestCase):
    """Test suite for task management endpoints"""

    def setUp(self):
        # Create test users and tasks
        self.user = User.objects.create_user(username="apiuser", password="apipass123")
        self.other_user = User.objects.create_user(
            username="another", password="pass123"
        )
        self.task = Task.objects.create(title="Existing Task", user=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)  # Authenticate primary user

    def test_create_task_authenticated(self):
        """Test task creation by authenticated user"""
        self.client.force_authenticate(user=self.user)
        data = {"title": "New Task", "description": "New description"}

        response = self.client.post("/api/tasks/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(response.data["user"], self.user.id)

    def test_create_task_unauthenticated(self):
        """Test task creation without authentication"""
        self.client.logout()  # Remove authentication

        # Try creating task without credentials
        data = {"title": "Should Fail"}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_invalid_data(self):
        """Test task creation with invalid data (missing title)"""
        # Send data without required 'title' field
        data = {"description": "Missing title"}
        response = self.client.post("/api/tasks/", data)

        # Verify validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_my_tasks_endpoint(self):
        """Test /api/tasks/my-tasks/ endpoint filtering"""
        # Create additional task for current user
        Task.objects.create(title="Another Task", user=self.user)
        response = self.client.get("/api/tasks/my-tasks/")

        # Verify correct task count (2 tasks)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_my_tasks_with_search_and_filter(self):
        """Test /api/tasks/my-tasks/ endpoint with search and filter parameters"""
        # Create additional tasks with different properties
        Task.objects.create(
            title="Shopping Task",
            description="Buy groceries",
            completed=True,
            user=self.user,
        )
        Task.objects.create(
            title="Work Task", description="Complete report", user=self.user
        )

        # Clear cache to avoid stale results
        cache.clear()

        # Test with search parameter
        response = self.client.get("/api/tasks/my-tasks/?search=Shopping")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Shopping Task")

        # Test with filter parameter
        response = self.client.get("/api/tasks/my-tasks/?completed=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Shopping Task")

    def test_filter_tasks_by_completion(self):
        """Test task filtering by completion status"""
        # Create completed task
        Task.objects.create(title="Completed Task", completed=True, user=self.user)

        # Filter completed tasks
        response = self.client.get("/api/tasks/?completed=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["completed"])

    def test_search_tasks(self):
        """Test task search by title/description"""
        # Create task with searchable content
        Task.objects.create(
            title="Shopping List", description="Groceries", user=self.user
        )

        # Perform search
        response = self.client.get("/api/tasks/?search=shopping")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_toggle_complete(self):
        """Test task completion status toggle"""
        # Toggle completion via endpoint
        url = f"/api/tasks/{self.task.id}/toggle-complete/"
        response = self.client.post(url)

        # Verify state change
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertTrue(self.task.completed)

    def test_toggle_complete_unauthorized(self):
        """Test toggle attempt on another user's task"""
        # Switch to different user
        self.client.force_authenticate(user=self.other_user)
        url = f"/api/tasks/{self.task.id}/toggle-complete/"
        response = self.client.post(url)

        # Verify permission denied (404 due to queryset filtering)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_task(self):
        """Test task deletion by owner"""
        # Delete owned task
        url = f"/api/tasks/{self.task.id}/"
        response = self.client.delete(url)

        # Verify deletion and database state
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_delete_other_user_task(self):
        """Test deletion attempt on another user's task"""
        # Create task for other user
        other_task = Task.objects.create(title="Other Task", user=self.other_user)
        url = f"/api/tasks/{other_task.id}/"
        response = self.client.delete(url)

        # Verify task still exists (404 response)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Task.objects.count(), 2)

    def test_update_task(self):
        """Test task update with valid data"""
        # Update task title
        url = f"/api/tasks/{self.task.id}/"
        data = {"title": "Updated Title"}
        response = self.client.patch(url, data)

        # Verify changes
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Title")

    def test_update_task_invalid_data(self):
        """Test task update with invalid data"""
        # Send empty title (invalid)
        url = f"/api/tasks/{self.task.id}/"
        data = {"title": ""}
        response = self.client.patch(url, data)

        # Verify validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
