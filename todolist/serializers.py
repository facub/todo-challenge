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

    def to_representation(self, instance):
        """Transform datetime to string representation"""
        representation = super().to_representation(instance)
        representation["created_at"] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        return representation

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
