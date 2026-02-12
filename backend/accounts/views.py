"""
Views for user authentication and management.
"""

from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserListSerializer,
    ChangePasswordSerializer,
    AdminUserUpdateSerializer,
)
from .permissions import IsAdminUser

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    Register a new user account.
    
    Creates a new user with the provided email, username, and password.
    Returns the created user details and JWT tokens for immediate access.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new user account",
        responses={
            201: openapi.Response(
                description="User registered successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "User registered successfully",
                        "data": {
                            "user": {
                                "id": 1,
                                "email": "user@example.com",
                                "username": "johndoe"
                            },
                            "tokens": {
                                "access": "eyJ...",
                                "refresh": "eyJ..."
                            }
                        }
                    }
                }
            ),
            400: "Bad Request - Validation errors"
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'username': user.username,
                        'role': user.role,
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(TokenObtainPairView):
    """
    Login with email and password to get JWT tokens.
    
    Returns access and refresh tokens along with user information.
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer
    
    @swagger_auto_schema(
        operation_description="Login to get JWT tokens",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "access": "eyJ...",
                        "refresh": "eyJ...",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "username": "johndoe",
                            "role": "user"
                        }
                    }
                }
            ),
            401: "Invalid credentials"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TokenRefreshAPIView(TokenRefreshView):
    """
    Refresh access token using refresh token.
    
    Returns a new access token (and optionally a new refresh token).
    """
    
    @swagger_auto_schema(
        operation_description="Refresh access token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
            }
        ),
        responses={
            200: openapi.Response(
                description="Token refreshed successfully",
                examples={
                    "application/json": {
                        "access": "eyJ...",
                        "refresh": "eyJ..."
                    }
                }
            ),
            401: "Invalid or expired refresh token"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutView(views.APIView):
    """
    Logout by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout and invalidate refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token to blacklist'),
            }
        ),
        responses={
            200: "Successfully logged out",
            400: "Bad Request"
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'success': False,
                    'message': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Get or update the authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_description="Get current user's profile",
        responses={
            200: UserProfileSerializer
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update current user's profile",
        responses={
            200: UserProfileSerializer
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Partially update current user's profile",
        responses={
            200: UserProfileSerializer
        }
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(generics.UpdateAPIView):
    """
    Change the authenticated user's password.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_description="Change password",
        responses={
            200: "Password changed successfully",
            400: "Bad Request - Validation errors"
        }
    )
    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.get_object()
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'success': True,
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Password change failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Admin Views
class AdminUserListView(generics.ListAPIView):
    """
    List all users (Admin only).
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserListSerializer
    
    @swagger_auto_schema(
        operation_description="List all users (Admin only)",
        responses={
            200: UserListSerializer(many=True),
            403: "Forbidden - Admin access required"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or delete a specific user (Admin only).
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminUserUpdateSerializer
    
    @swagger_auto_schema(
        operation_description="Get user details (Admin only)",
        responses={
            200: AdminUserUpdateSerializer,
            403: "Forbidden - Admin access required",
            404: "User not found"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Update user (Admin only)",
        responses={
            200: AdminUserUpdateSerializer,
            403: "Forbidden - Admin access required",
            404: "User not found"
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_description="Delete user (Admin only)",
        responses={
            204: "User deleted successfully",
            403: "Forbidden - Admin access required",
            404: "User not found"
        }
    )
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({
                'success': False,
                'message': 'You cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().delete(request, *args, **kwargs)
