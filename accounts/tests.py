# Standard imports
from datetime import timedelta
from unittest.mock import patch

# Django imports
from django.urls import reverse
from django.contrib.auth.models import User

# External imports
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError


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
        response = self.client.post("/api/accounts/register/", data)

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
