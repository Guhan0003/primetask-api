"""
Custom User Model with Role-Based Access Control.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with role field for role-based access control.
    
    Roles:
    - user: Regular user with limited access
    - admin: Administrator with full access
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True, help_text="User's email address (unique)")
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        help_text="User role for access control"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the primary identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == 'admin'
    
    @property
    def is_regular_user(self):
        """Check if user has regular user role."""
        return self.role == 'user'
