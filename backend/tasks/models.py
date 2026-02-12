"""
Task Model for Task Management.
"""

from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Task model for task management system.
    
    Each task belongs to a user and has a status for tracking progress.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Task title"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Task description"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the task"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Task priority level"
    )
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Task due date"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="User who owns this task"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.status})"
