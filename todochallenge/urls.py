# Django imports
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

# External imports
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API URLs
    path("api/", include("todolist.urls")),
    # JWT Auth URLs
    path("api/accounts/", include("accounts.urls")),
]

urlpatterns += [
    # Frontend Pages
    path(
        "register/",
        TemplateView.as_view(template_name="register.html"),
        name="register-page",
    ),
    path("login/", TemplateView.as_view(template_name="login.html"), name="login-page"),
    path(
        "logout/", TemplateView.as_view(template_name="login.html"), name="logout-page"
    ),
    path(
        "tasks/",
        TemplateView.as_view(template_name="tasks/list.html"),
        name="task-list",
    ),
    path(
        "tasks/create/",
        TemplateView.as_view(template_name="tasks/create.html"),
        name="task-create",
    ),
    path(
        "categories/",
        TemplateView.as_view(template_name="categories/list.html"),
        name="category-list",
    ),
    path(
        "categories/create/",
        TemplateView.as_view(template_name="categories/create.html"),
        name="category-create",
    ),
]
