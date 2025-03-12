# Stantard imports
import logging

# External imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

# App imports
from .models import Task
from .serializers import TaskSerializer
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
    search_fields = ["title", "description"]

    def get_queryset(self):
        """Optimized queryset with select_related"""
        # Fetch tasks for authenticated user
        tasks = Task.objects.filter(user=self.request.user).select_related("user")
        logger.info(
            f"TASKS_FETCHED: Count={tasks.count()} | User={self.request.user.id}"
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
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update task and log changes"""
        # Save updated task
        task = serializer.save()
        logger.info(
            f"TASK UPDATED: ID={task.id} | "
            f"Title='{task.title}' | Completed={task.completed}"
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

        # Apply filters
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

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

        # Save task with updated completion status
        task.save(update_fields=["completed"])

        logger.info(
            f"TOGGLE COMPLETE: Task ID={task.id} | "
            f"From {previous_state} to {task.completed}"
        )

        return Response(
            {
                "status": "success",
                "completed": task.completed,
                "message": f"Task marked as {'completed' if task.completed else 'pending'}",
            },
            status=status.HTTP_200_OK,
        )
