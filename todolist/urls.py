# Django imports
from django.urls import path, include

# External imports
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet,
    TaskCategoryViewSet,
)

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"categories", TaskCategoryViewSet, basename="category")

urlpatterns = [
    # API Endpoints
    path("", include(router.urls)),
]
