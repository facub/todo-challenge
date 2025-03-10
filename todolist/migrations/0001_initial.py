# Generated by Django 4.2.12 on 2025-03-06 22:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="Short description of the task", max_length=200
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Detailed task description (optional)"
                    ),
                ),
                (
                    "completed",
                    models.BooleanField(
                        default=False, help_text="Indicates if the task is finished"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when the task was created",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="Owner of the task",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
