# External imports
from rest_framework import serializers

# App imports
from .models import Task, TaskCategory, PRIORITY_CHOICES


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model. Handles validation and data transformation.
    """

    category = serializers.PrimaryKeyRelatedField(
        queryset=TaskCategory.objects.all(),
        allow_null=True,
        required=False,
        help_text="Category associated with the task",
    )
    priority = serializers.ChoiceField(
        choices=PRIORITY_CHOICES,
        default="medium",
        help_text="Priority level of the task",
    )
    due_date = serializers.DateField(
        allow_null=True,
        required=False,
        help_text="Due date for the task",
    )
    completed_at = serializers.DateTimeField(
        read_only=True,
        help_text="Timestamp when the task was marked as completed",
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "completed",
            "created_at",
            "user",
            "category",
            "priority",
            "due_date",
            "completed_at",
        ]
        read_only_fields = ["id", "created_at", "user", "completed_at"]
        extra_kwargs = {
            "description": {"required": False},
            "completed": {"read_only": True},
        }

    def to_representation(self, instance):
        """Transform datetime to string representation"""
        representation = super().to_representation(instance)
        representation["created_at"] = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
        if instance.completed_at:
            representation["completed_at"] = instance.completed_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        if instance.category:
            representation["category"] = instance.category.name
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


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = ["id", "name"]
