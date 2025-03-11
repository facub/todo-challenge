from .local import *

# Testing settings
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "todo_db",
        "USER": "todo_user",
        "PASSWORD": "todo_password",
        "HOST": "todo_db",
        "PORT": "5432",
    }
}
