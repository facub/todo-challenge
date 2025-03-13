# Standard imports
from datetime import timedelta

# Django imports
from django.urls import reverse
from django.contrib.auth.models import User

# External imports
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


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
