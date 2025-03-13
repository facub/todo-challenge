# Django imports
from django_filters import FilterSet, DateFilter, ChoiceFilter

# App imports
from .models import Task, PRIORITY_CHOICES


class TaskFilter(FilterSet):
    created_at = DateFilter(field_name="created_at", lookup_expr="date")
    priority = ChoiceFilter(choices=PRIORITY_CHOICES)
    due_date_before = DateFilter(field_name="due_date", lookup_expr="lte")
    due_date_after = DateFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = [
            "completed",
            "created_at",
            "priority",
            "due_date_before",
            "due_date_after",
        ]
