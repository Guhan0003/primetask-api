"""
Serializers for User authentication and management.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password validation.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password (min 8 characters)"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm password"
    )
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate_email(self, value):
        """Validate email is unique and properly formatted."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username is unique and alphanumeric."""
        if User.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if not value.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value.lower()
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create a new user with hashed password."""
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='user'  # Default role
        )
        return user


class UserLoginSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user info in response.
    """
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to token
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role
        
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add user info to response
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
            'username': self.user.username,
            'role': self.user.role,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile (read/update).
    """
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'created_at', 'updated_at']
        read_only_fields = ['id', 'email', 'role', 'created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (admin only).
    """
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_active', 'created_at', 'tasks_count']
        read_only_fields = fields
    
    def get_tasks_count(self, obj):
        """Get count of tasks owned by user."""
        return obj.tasks.count() if hasattr(obj, 'tasks') else 0


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate new password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate old password and confirm new passwords match."""
        user = self.context['request'].user
        
        if not user.check_password(attrs['old_password']):
            raise serializers.ValidationError({
                'old_password': "Current password is incorrect."
            })
        
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New passwords do not match."
            })
        
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({
                'new_password': "New password must be different from current password."
            })
        
        return attrs


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to update user details.
    """
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role', 'is_active']
        read_only_fields = ['id', 'email', 'username']
