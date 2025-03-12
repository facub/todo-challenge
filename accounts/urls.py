# Django imports
from django.urls import path

# App imports
from .views import UserRegistrationView, UserLoginView, CheckAuthView, UserLogoutView

urlpatterns = [
    # Authentication
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("check-auth/", CheckAuthView.as_view(), name="check-auth"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
]
