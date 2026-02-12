"""
URL configuration for PrimeTask API project.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="PrimeTask API",
        default_version='v1',
        description="""
        # PrimeTask API Documentation
        
        A scalable REST API with authentication and role-based access control.
        
        ## Features
        - User Registration & Login with JWT Authentication
        - Role-based Access Control (User vs Admin)
        - Task Management CRUD Operations
        - API Versioning
        - Input Validation & Error Handling
        
        ## Authentication
        This API uses JWT (JSON Web Tokens) for authentication.
        1. Register a new account or login to get tokens
        2. Include the access token in the Authorization header: `Bearer <token>`
        3. Refresh tokens when they expire using the refresh endpoint
        
        ## Roles
        - **User**: Can manage their own tasks
        - **Admin**: Can manage all users and tasks
        """,
        terms_of_service="https://www.primetrade.ai/terms/",
        contact=openapi.Contact(email="support@primetrade.ai"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API v1 endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/tasks/', include('tasks.urls')),
    
    # Swagger Documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Root redirect to swagger
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='api-root'),
]
