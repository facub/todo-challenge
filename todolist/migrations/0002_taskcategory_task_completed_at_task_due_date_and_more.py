# Generated by Django 4.2.12 on 2025-03-12 23:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("todolist", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskCategory",
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
                    "name",
                    models.CharField(
                        help_text="Category name", max_length=50, unique=True
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="task",
            name="completed_at",
            field=models.DateTimeField(
                blank=True,
                help_text="Timestamp when the task was marked as completed",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="due_date",
            field=models.DateField(
                blank=True, help_text="Due date for the task (optional)", null=True
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="priority",
            field=models.CharField(
                choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                default="medium",
                help_text="Priority level for the task",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="category",
            field=models.ForeignKey(
                blank=True,
                help_text="Category or tag for the task",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tasks",
                to="todolist.taskcategory",
            ),
        ),
    ]
