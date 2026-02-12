"""
Custom permissions for role-based access control.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class that only allows admin users.
    """
    message = "You must be an admin to perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class that allows object owners or admin users.
    """
    message = "You do not have permission to access this resource."
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == 'admin':
            return True
        
        # Check if the user is the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    Permission class that only allows object owners.
    """
    message = "You can only access your own resources."
    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class ReadOnly(permissions.BasePermission):
    """
    Permission class that only allows read-only access.
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
