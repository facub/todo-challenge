# Stantard imports
import logging
# Django imports
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# External imports
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter
# App imports
from .models import Task
from .serializers import TaskSerializer, UserSerializer


# Logger configuration
logger = logging.getLogger(__name__)


class UserLoginView(APIView):
    """User login endpoint to obtain JWT token"""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        
        return Response({'error': 'Invalid credentials'}, status=401)


class UserRegistrationView(APIView):
    """
    User Registration Endpoint
    Provides user creation functionality with JWT authentication
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access

    def post(self, request):
        """
        Handle user registration requests
        ---
        Request Body:
            {
                "username": "string",
                "password": "string"
            }
        """
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"USER_REGISTERED: ID={user.id} | Username={user.username}")
            
            # Return user data without password
            response_data = {
                "id": user.id,
                "username": user.username,
                "message": "User created successfully"
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"REGISTRATION_FAILED: Errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing user tasks.
    Provides CRUD operations and custom actions.
    """
    
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["completed", "created_at"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        """Optimized queryset with select_related"""
        import ipdb; ipdb.set_trace()
        tasks = Task.objects.filter(user=self.request.user).select_related('user')
        logger.info(f"TASKS_FETCHED: Count={tasks.count()} | User={self.request.user.id}")
        return tasks

    def perform_create(self, serializer):
        """Deny task creation for unauthenticated users"""
        if not self.request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update task and log changes"""
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
        filter_backends = [DjangoFilterBackend, SearchFilter]
        for backend in filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        logger.info(f"MY_TASKS_FILTERED: Count={queryset.count()}")

        # Serialize and return response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="toggle-complete")
    def toggle_complete(self, request, pk=None):
        """
        Toggle task completion status.
        Endpoint: /api/tasks/{id}/toggle-complete/
        """
        task = self.get_object()
        previous_state = task.completed
        task.completed = not task.completed
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
