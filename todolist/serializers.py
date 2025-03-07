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
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "user"
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "user": {"write_only": True}  # User is automatically set in view
        }

    def validate_title(self, value):
        """Ensure title is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value

    def validate_description(self, value):
        """Ensure description is not empty"""
        if value is not None and not value.strip():
            raise serializers.ValidationError("Description cannot be empty")
        return value

    def create(self, validated_data):
        """
        Create a new task with the validated data.
        Automatically sets the user from the request context.
        """
        # Obtener el usuario desde el contexto (request.user)
        user = self.context["user"]
        return Task.objects.create(user=user, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model. Handles validation and data transformation.
    """
    
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(**validated_data)
        return user
