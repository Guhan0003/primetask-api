"""
URL patterns for task management endpoints.
"""

from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    TaskStatsView,
    AdminTaskListView,
    AdminTaskDeleteView,
)

app_name = 'tasks'

urlpatterns = [
    # Task CRUD endpoints
    path('', TaskListCreateView.as_view(), name='task_list_create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('stats/', TaskStatsView.as_view(), name='task_stats'),
    
    # Admin endpoints
    path('admin/all/', AdminTaskListView.as_view(), name='admin_task_list'),
    path('admin/<int:pk>/delete/', AdminTaskDeleteView.as_view(), name='admin_task_delete'),
]
