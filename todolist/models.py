# Stantard imports
import logging
# Django imports
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


# Logger configuration
logger = logging.getLogger(__name__)


class Task(models.Model):
    """
    Task model representing user tasks with completion status and timestamps.
    """
    
    title = models.CharField(max_length=200, help_text="Short description of the task")
    description = models.TextField(blank=True, help_text="Detailed task description (optional)")
    completed = models.BooleanField(default=False, help_text="Indicates if the task is finished")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the task was created")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", help_text="Owner of the task")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({'Completed' if self.completed else 'Pending'})"

    def save(self, *args, **kwargs):
        """Log task creation/update events"""
        if not self.pk:
            logger.info(f"TASK CREATED: '{self.title}' by user {self.user}")
        else:
            logger.info(f"TASK UPDATED: '{self.title}' (ID: {self.pk})")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Log task deletion events"""
        logger.warning(f"TASK DELETED: '{self.title}' (ID: {self.pk})")
        super().delete(*args, **kwargs)
