# Django imports
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory

# App imports
from todolist.admin import TaskAdmin
from todolist.models import Task


class TestTaskAdmin(TestCase):
    """Test suite for the TaskAdmin class"""

    def setUp(self):
        # Create users
        self.superuser = User.objects.create_superuser(
            username="superuser", password="superpass123"
        )
        self.regular_user = User.objects.create_user(
            username="regularuser", password="regularpass123"
        )

        # Create tasks
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            user=self.regular_user,
            completed=False,
        )

        # Configure the admin site
        self.admin_site = None  # The admin site is not necessary for these tests
        self.task_admin = TaskAdmin(Task, self.admin_site)

        # Configure the RequestFactory
        self.factory = RequestFactory()

    def test_get_readonly_fields_superuser(self):
        """
        Test that superusers have no readonly fields.
        """
        request = self.factory.get("/admin/tasks/task/")
        request.user = self.superuser
        readonly_fields = self.task_admin.get_readonly_fields(request)
        self.assertEqual(readonly_fields, [])

    def test_get_readonly_fields_regular_user(self):
        """
        Test that regular users have readonly fields.
        """
        request = self.factory.get("/admin/tasks/task/")
        request.user = self.regular_user
        readonly_fields = self.task_admin.get_readonly_fields(request)
        self.assertEqual(readonly_fields, ["created_at"])

    def test_save_model_assigns_user(self):
        """
        Test that the user is assigned when saving a new task.
        """
        request = self.factory.post("/admin/tasks/task/add/")
        request.user = self.regular_user

        # Create a new task without assigning a user
        obj = Task(title="New Task", description="New Description")
        form = None  # The form is not necessary for this test

        # Save the model
        self.task_admin.save_model(request, obj, form, change=False)

        # Verify that the user was assigned correctly
        self.assertEqual(obj.user, self.regular_user)

    def test_save_model_does_not_override_user(self):
        """
        Test that the user is not overridden when editing an existing task.
        """
        request = self.factory.post(f"/admin/tasks/task/{self.task.id}/change/")
        request.user = self.superuser

        # Edit an existing task
        obj = self.task
        form = None  # The form is not necessary for this test

        # Save the model
        self.task_admin.save_model(request, obj, form, change=True)

        # Verify that the user did not change
        self.assertEqual(obj.user, self.regular_user)

    def test_get_queryset_superuser(self):
        """
        Test that superusers can see all tasks.
        """
        request = self.factory.get("/admin/tasks/task/")
        request.user = self.superuser
        queryset = self.task_admin.get_queryset(request)
        self.assertEqual(queryset.count(), 1)  # Only one task in the database

    def test_get_queryset_regular_user(self):
        """
        Test that regular users can only see their own tasks.
        """
        # Create a task for another user
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )
        Task.objects.create(
            title="Other Task",
            description="Other Description",
            user=other_user,
            completed=False,
        )

        request = self.factory.get("/admin/tasks/task/")
        request.user = self.regular_user
        queryset = self.task_admin.get_queryset(request)

        # Verify that only the current user's tasks are shown
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().user, self.regular_user)

    def test_has_change_permission_superuser(self):
        """
        Test that superusers can change any task.
        """
        request = self.factory.get(f"/admin/tasks/task/{self.task.id}/change/")
        request.user = self.superuser
        has_permission = self.task_admin.has_change_permission(request, obj=self.task)
        self.assertFalse(has_permission)

    def test_has_change_permission_regular_user_own_task(self):
        """
        Test that regular users can change their own tasks.
        """
        request = self.factory.get(f"/admin/tasks/task/{self.task.id}/change/")
        request.user = self.regular_user
        has_permission = self.task_admin.has_change_permission(request, obj=self.task)
        self.assertFalse(has_permission)

    def test_has_change_permission_regular_user_other_task(self):
        """
        Test that regular users cannot change other users' tasks.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )
        other_task = Task.objects.create(
            title="Other Task",
            description="Other Description",
            user=other_user,
            completed=False,
        )

        request = self.factory.get(f"/admin/tasks/task/{other_task.id}/change/")
        request.user = self.regular_user
        has_permission = self.task_admin.has_change_permission(request, obj=other_task)
        self.assertFalse(has_permission)

    def test_has_delete_permission_superuser(self):
        """
        Test that superusers can delete any task.
        """
        request = self.factory.get(f"/admin/tasks/task/{self.task.id}/delete/")
        request.user = self.superuser
        has_permission = self.task_admin.has_delete_permission(request, obj=self.task)
        self.assertFalse(has_permission)

    def test_has_delete_permission_regular_user_own_task(self):
        """
        Test that regular users can delete their own tasks.
        """
        request = self.factory.get(f"/admin/tasks/task/{self.task.id}/delete/")
        request.user = self.regular_user
        has_permission = self.task_admin.has_delete_permission(request, obj=self.task)
        self.assertFalse(has_permission)

    def test_has_delete_permission_regular_user_other_task(self):
        """
        Test that regular users cannot delete other users' tasks.
        """
        other_user = User.objects.create_user(
            username="otheruser", password="otherpass123"
        )
        other_task = Task.objects.create(
            title="Other Task",
            description="Other Description",
            user=other_user,
            completed=False,
        )

        request = self.factory.get(f"/admin/tasks/task/{other_task.id}/delete/")
        request.user = self.regular_user
        has_permission = self.task_admin.has_delete_permission(request, obj=other_task)
        self.assertFalse(has_permission)
