# Django imports
from django_filters import (
    FilterSet,
    DateFilter,
    ChoiceFilter,
    CharFilter,
    BooleanFilter,
)

# App imports
from .models import Task, PRIORITY_CHOICES


class TaskFilter(FilterSet):
    title = CharFilter(field_name="title", lookup_expr="icontains")
    created_at = DateFilter(field_name="created_at", lookup_expr="date")
    completed_at = DateFilter(field_name="completed_at", lookup_expr="date")
    due_date = DateFilter(field_name="due_date")
    priority = ChoiceFilter(choices=PRIORITY_CHOICES)
    completed = BooleanFilter()

    class Meta:
        model = Task
        fields = [
            "title",
            "created_at",
            "completed_at",
            "due_date",
            "priority",
            "completed",
        ]
