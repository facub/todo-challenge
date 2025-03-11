# Django imports
from django_filters import FilterSet, DateFilter

# App imports
from .models import Task


class TaskFilter(FilterSet):
    created_at = DateFilter(field_name="created_at", lookup_expr="date")

    class Meta:
        model = Task
        fields = ["completed", "created_at"]
