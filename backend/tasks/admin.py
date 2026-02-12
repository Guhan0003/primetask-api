from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for Task model.
    """
    list_display = ['title', 'owner', 'status', 'priority', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description', 'owner__email', 'owner__username']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'status', 'priority', 'due_date')
        }),
        ('Ownership', {
            'fields': ('owner',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
