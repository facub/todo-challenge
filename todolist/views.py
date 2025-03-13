# Stantard imports
import logging

# External imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

# Django imports
from django.utils import timezone

# App imports
from .models import Task, TaskCategory
from .serializers import TaskSerializer, TaskCategorySerializer
from .filters import TaskFilter


# Logger configuration
logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user tasks.
    Provides CRUD operations and custom actions.
    """

    queryset = Task.objects.all()
    pagination_class = StandardResultsSetPagination
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = TaskFilter
    search_fields = [
        "title",
        "description",
        "category__name",
        "priority",
        "due_date",
        "completed",
        "created_at",
        "completed_at",
    ]

    def get_queryset(self):
        """Optimized queryset with select_related"""
        tasks = Task.objects.filter(user=self.request.user).select_related(
            "user", "category"
        )
        logger.info(
            f"TASKS_FETCHED: Count={tasks.count()} | User={self.request.user.id} | "
            f"Priorities={[task.priority for task in tasks]} | "
            f"Due Dates={[task.due_date for task in tasks]}"
        )
        return tasks

    def get_serializer_context(self):
        """
        Incluir request en el contexto del serializador
        """
        return {"request": self.request}

    def perform_create(self, serializer):
        """Deny task creation for unauthenticated users"""
        # Save task with authenticated user
        category = None
        if self.request.data.get("category"):
            category = TaskCategory.objects.get(id=self.request.data.get("category"))
        serializer.save(
            user=self.request.user,
            category=category,
            priority=self.request.data.get("priority"),
            due_date=self.request.data.get("due_date"),
        )

    def perform_update(self, serializer):
        """Update task and log changes"""
        # Save updated task
        task = serializer.save()
        logger.info(
            f"TASK UPDATED: ID={task.id} | "
            f"Title='{task.title}' | Completed={task.completed} | "
            f"Priority={task.priority} | Due Date={task.due_date}"
        )

    def perform_destroy(self, instance):
        """Delete task and log event"""
        logger.warning(
            f"TASK DELETED: ID={instance.id} | "
            f"Title='{instance.title}' | User={instance.user.id}"
        )
        # Delete task
        instance.delete()

    @action(detail=False, methods=["get"], url_path="my-tasks")
    def my_tasks(self, request):
        """
        List tasks of the authenticated user with optional filters.
        Endpoint: /api/tasks/my-tasks/
        """
        # Get authenticated user's tasks
        queryset = Task.objects.filter(user=request.user)

        logger.info(f"MY_TASKS: Count={queryset.count()} | User={request.user.id}")

        # Apply filters using self.filter_queryset
        queryset = self.filter_queryset(queryset)

        logger.info(f"MY_TASKS_FILTERED: Count={queryset.count()}")

        # Serialize and return response
        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"MY_TASKS: Cache set | User={request.user.id}")
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="toggle-complete")
    def toggle_complete(self, request, pk=None):
        """
        Toggle task completion status.
        Endpoint: /api/tasks/{id}/toggle-complete/
        """
        # Get task and toggle completion status
        task = self.get_object()
        previous_state = task.completed
        task.completed = not task.completed

        # Update completed_at if task is marked as completed
        if task.completed:
            task.completed_at = timezone.now()
        else:
            task.completed_at = None

        # Save task with updated completion status
        task.save(update_fields=["completed", "completed_at"])

        logger.info(
            f"TOGGLE COMPLETE: Task ID={task.id} | "
            f"From {previous_state} to {task.completed} | "
            f"Completed At={task.completed_at}"
        )

        return Response(
            {
                "status": "success",
                "completed": task.completed,
                "message": f"Task marked as {'completed' if task.completed else 'pending'}",
            },
            status=status.HTTP_200_OK,
        )


class TaskCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage Task Categories.
    Provides CRUD operations for categories associated with the authenticated user.
    """

    serializer_class = TaskCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return categories filtered by the authenticated user.
        """
        return TaskCategory.objects.all()

    def perform_create(self, serializer):
        """
        Associate the category with the authenticated user on creation.
        """
        serializer.save()

    @action(detail=False, methods=["get"], url_path="all")
    def get_all_categories(self, request):
        """
        Endpoint to fetch all categories (without user filtering).
        Endpoint: /api/categories/all/
        """
        categories = TaskCategory.objects.all()
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["delete"], url_path="delete")
    def custom_delete(self, request, pk=None):
        """
        Custom delete action for a specific category.
        Endpoint: /api/categories/{id}/delete/
        """
        category = self.get_object()
        category.delete()
        return Response(
            {"message": "Category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
