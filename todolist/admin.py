# Django imports
from django.contrib import admin

# App imports
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for Task model.
    """

    list_display = ["id", "title", "description", "completed", "created_at", "user"]
    list_filter = ["completed", "created_at"]
    search_fields = ["title", "description"]
    list_per_page = 10
    list_display_links = ["id", "title"]
    list_editable = ["completed"]
    readonly_fields = ["created_at"]

    def get_readonly_fields(self, request, obj=None):
        """
        Return readonly fields based on user permissions.
        """
        if request.user.is_superuser:
            return []
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        """
        Save model with user information.
        """
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """
        Filter queryset based on user permissions.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def has_change_permission(self, request, obj=None):
        """
        Check if user has permission to change object.
        """
        if obj and not obj.user == request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Check if user has permission to delete object.
        """
        if obj and not obj.user == request.user:
            return False
        return super().has_delete_permission(request, obj)
