# Django imports
from django.contrib.auth.models import User

# External imports
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

# App imports
from todolist.models import Task, TaskCategory


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
        data = {
            "title": "New Task",
            "description": "New description",
            "priority": "low",
        }

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

    def test_toggle_pending(self):
        """Test task completion status toggle"""
        # Toggle completion via endpoint
        self.task.completed = True
        self.task.save()
        url = f"/api/tasks/{self.task.id}/toggle-complete/"
        response = self.client.post(url)

        # Verify state change
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertFalse(self.task.completed)

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

    def test_task_creation_with_category_and_due_date(self):
        """Test task creation with category, priority, and due date"""
        category = TaskCategory.objects.create(name="Work")
        data = {
            "title": "New Task",
            "description": "With category and due date",
            "category": category.id,
            "priority": "high",
            "due_date": "2023-12-31",
        }
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task = Task.objects.get(id=response.data["id"])
        self.assertEqual(task.category.id, category.id)
        self.assertEqual(task.priority, "high")
        self.assertEqual(str(task.due_date), "2023-12-31")
