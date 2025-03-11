# Django imports
from django.urls import path, include

# External imports
from rest_framework.routers import DefaultRouter
from .views import (
    TaskViewSet,
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    CheckAuthView,
)

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")

urlpatterns = [
    # API Endpoints
    path("", include(router.urls)),
    # Authentication
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("check-auth/", CheckAuthView.as_view(), name="check-auth"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
]
