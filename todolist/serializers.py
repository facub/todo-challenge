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
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "description": {"required": False},
            "completed": {"read_only": True},
        }

    def validate_description(self, value):
        """Ensure description is not empty"""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value


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
