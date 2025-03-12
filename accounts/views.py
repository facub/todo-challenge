# Stantard imports
import logging

# Django imports
from django.contrib.auth import authenticate

# External imports
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

# App imports
from .serializers import UserSerializer


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
    Endpoint: GET /api/accounts/check-auth/
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
                    ),  # Expiration timestamp
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
