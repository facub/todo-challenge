# Stantard imports
import logging

# Django imports
from django.contrib.auth import authenticate

# External imports
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# App imports
from .models import Task
from .serializers import TaskSerializer, UserSerializer


# Logger configuration
logger = logging.getLogger(__name__)


class UserLoginView(APIView):
    """User login endpoint to obtain JWT token"""

    permission_classes = [AllowAny]

    def post(self, request):
        """
        User Login Endpoint
        Provides user authentication with JWT token
        """
        # Get username and password from request
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate user and generate JWT token
        user = authenticate(username=username, password=password)
        if user:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            # Return token pair
            return Response(
                {"access": str(refresh.access_token), "refresh": str(refresh)}
            )

        return Response({"error": "Invalid credentials"}, status=401)


class UserRegistrationView(APIView):
    """
    User Registration Endpoint
    Provides user creation functionality with JWT authentication
    """

    permission_classes = [AllowAny]  # Allow unauthenticated access

    def post(self, request):
        """
        Handle user registration requests
        """
        # Validate user data and create user
        serializer = UserSerializer(data=request.data)

        # Validate and save user data
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"USER_REGISTERED: ID={user.id} | Username={user.username}")

            # Return user data without password
            response_data = {
                "id": user.id,
                "username": user.username,
                "message": "User created successfully",
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        logger.warning(f"REGISTRATION_FAILED: Errors={serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckAuthView(APIView):
    """
    Verify user authentication status and return session information
    Endpoint: GET /api/check-auth/
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Return authentication status and user details
        """
        # Get current access token from request
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response({"error": "Authorization header missing"}, status=401)

        try:
            # Extract token from header and decode payload
            token = auth_header.split(" ")[1]
            access_token = AccessToken(token)

            return Response(
                {
                    "authenticated": True,
                    "user_id": request.user.id,
                    "username": request.user.username,
                    "token_expires": access_token.payload.get(
                        "exp"
                    ),  # Timestamp de expiración
                }
            )
        except TokenError:
            return Response({"error": "Invalid token"}, status=401)


class UserLogoutView(APIView):
    """
    User Logout Endpoint
    Provides user logout functionality by blacklisting JWT token
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Handle user logout requests
        """
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": "Server error during logout"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
    filterset_fields = ["completed", "created_at"]
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
        filter_backends = [DjangoFilterBackend, SearchFilter]
        for backend in filter_backends:
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
