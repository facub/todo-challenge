from .local import *

# Testing settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_todo_db",
        "USER": "test_user",
        "PASSWORD": "test_password",
        "HOST": "test-db",
        "PORT": "5432",
        "TEST": {
            "NAME": "test_test_todo_db",
        },
    }
}

# Disable cache for testing
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Use the pytest test runner
TEST_RUNNER = "pytest_django.runner.DiscoverRunner"
