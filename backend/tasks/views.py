"""
Views for Task management.
"""

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Task
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskListSerializer,
    TaskStatsSerializer,
)
from accounts.permissions import IsOwnerOrAdmin, IsAdminUser


class TaskListCreateView(generics.ListCreateAPIView):
    """
    List all tasks for the current user or create a new task.
    
    - Regular users: See only their own tasks
    - Admin users: See all tasks
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskListSerializer
    
    def get_queryset(self):
        """
        Filter tasks based on user role and query parameters.
        """
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
        
        user = self.request.user
        
        # Admin sees all tasks, regular users see only their own
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'admin':
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(owner=user)
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        priority_filter = self.request.query_params.get('priority')
        search = self.request.query_params.get('search')
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="List all tasks (filtered by role)",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description="Filter by status (pending, in_progress, completed, cancelled)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'priority',
                openapi.IN_QUERY,
                description="Filter by priority (low, medium, high)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in title and description",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: TaskListSerializer(many=True)
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Create a new task",
        request_body=TaskCreateSerializer,
        responses={
            201: TaskSerializer,
            400: "Bad Request - Validation errors"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response({
                'success': True,
                'message': 'Task created successfully',
                'data': TaskSerializer(task).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Task creation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific task.
    
    - Regular users: Can only access their own tasks
    - Admin users: Can access any task
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        """Get task queryset based on user role."""
        # Handle swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()
        
        user = self.request.user
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'admin':
            return Task.objects.all()
        return Task.objects.filter(owner=user)
    
    @swagger_auto_schema(
        operation_description="Get task details",
        responses={
            200: TaskSerializer,
            404: "Task not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update task (full update)",
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: "Bad Request - Validation errors",
            404: "Task not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update task (partial update)",
        request_body=TaskSerializer,
        responses={
            200: TaskSerializer,
            400: "Bad Request - Validation errors",
            404: "Task not found"
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete task",
        responses={
            204: "Task deleted successfully",
            404: "Task not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class TaskStatsView(views.APIView):
    """
    Get task statistics for the current user.
    
    - Regular users: Stats for their own tasks
    - Admin users: Stats for all tasks
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Get task statistics",
        responses={
            200: TaskStatsSerializer
        }
    )
    def get(self, request):
        user = request.user
        
        # Filter based on role
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'admin':
            queryset = Task.objects.all()
        else:
            queryset = Task.objects.filter(owner=user)
        
        # Calculate statistics
        stats = {
            'total': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'in_progress': queryset.filter(status='in_progress').count(),
            'completed': queryset.filter(status='completed').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
        }
        
        return Response({
            'success': True,
            'data': stats
        })


# Admin-specific views
class AdminTaskListView(generics.ListAPIView):
    """
    List all tasks in the system (Admin only).
    """
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = TaskListSerializer
    
    @swagger_auto_schema(
        operation_description="List all tasks (Admin only)",
        responses={
            200: TaskListSerializer(many=True),
            403: "Forbidden - Admin access required"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminTaskDeleteView(generics.DestroyAPIView):
    """
    Delete any task (Admin only).
    """
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Delete any task (Admin only)",
        responses={
            204: "Task deleted successfully",
            403: "Forbidden - Admin access required",
            404: "Task not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        task.delete()
        return Response({
            'success': True,
            'message': 'Task deleted successfully'
        }, status=status.HTTP_200_OK)
