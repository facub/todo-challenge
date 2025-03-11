# Django imports
from django.contrib.auth.models import User

# External imports
from rest_framework import serializers

# App imports
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model. Handles validation and data transformation.
    """

    class Meta:
        model = Task
        fields = ["id", "title", "description", "completed", "created_at", "user"]
        read_only_fields = ["id", "created_at", "user"]
        extra_kwargs = {
            "description": {"required": False},
            "completed": {"read_only": True},
        }

    def validate_description(self, value):
        """Ensure description is not empty"""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value

    def validate(self, data):
        """
        Validate user authentication and request context
        """
        request = self.context.get("request")

        # Check if request context exists
        if not request:
            raise serializers.ValidationError("Request context not found")

        # Check if user is authenticated
        if not request.user.is_authenticated:
            raise serializers.ValidationError("User authentication required")

        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model. Handles validation and data transformation.
    """

    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(**validated_data)
        return user
