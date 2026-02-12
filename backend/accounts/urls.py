"""
URL patterns for authentication endpoints.
"""

from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    TokenRefreshAPIView,
    LogoutView,
    UserProfileView,
    ChangePasswordView,
    AdminUserListView,
    AdminUserDetailView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshAPIView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Admin endpoints
    path('admin/users/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]
