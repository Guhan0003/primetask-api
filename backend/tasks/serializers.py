"""
Serializers for Task management.
"""

from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task CRUD operations.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'due_date',
            'owner',
            'owner_email',
            'owner_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def validate_title(self, value):
        """Validate task title."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long."
            )
        return value.strip()
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:  # Update operation
            current_status = self.instance.status
            # Define allowed transitions
            allowed_transitions = {
                'pending': ['in_progress', 'cancelled'],
                'in_progress': ['completed', 'pending', 'cancelled'],
                'completed': ['pending'],  # Can reopen
                'cancelled': ['pending'],  # Can reopen
            }
            if value != current_status and value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from '{current_status}' to '{value}'."
                )
        return value


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks.
    """
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date']
    
    def validate_title(self, value):
        """Validate task title."""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long."
            )
        return value.strip()
    
    def create(self, validated_data):
        """Create task with the current user as owner."""
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing tasks.
    """
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'status',
            'priority',
            'due_date',
            'owner_username',
            'created_at',
        ]


class TaskStatsSerializer(serializers.Serializer):
    """
    Serializer for task statistics.
    """
    total = serializers.IntegerField()
    pending = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    completed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
