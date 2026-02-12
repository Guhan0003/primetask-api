# 📘 Technical Documentation

## PrimeTask API - Backend Developer Internship Assignment

**Author:** Guhan S  
**Date:** February 2026  
**Version:** 1.0.0

---

## 📑 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Design](#2-architecture-design)
3. [Authentication System](#3-authentication-system)
4. [Role-Based Access Control](#4-role-based-access-control)
5. [API Design & Versioning](#5-api-design--versioning)
6. [Database Design](#6-database-design)
7. [Error Handling](#7-error-handling)
8. [Security Implementation](#8-security-implementation)
9. [Scalability Considerations](#9-scalability-considerations)
10. [Testing Strategy](#10-testing-strategy)
11. [Deployment Guide](#11-deployment-guide)

---

## 1. Project Overview

### 1.1 Objective

Build a scalable REST API with:
- User authentication using JWT
- Role-based access control (User/Admin)
- CRUD operations for task management
- API versioning and documentation
- Basic frontend integration

### 1.2 Assignment Requirements Mapping

| Requirement | Implementation | File Location |
|-------------|----------------|---------------|
| JWT Authentication | SimpleJWT with access/refresh tokens | `accounts/views.py` |
| Role-Based Access | Custom permission classes | `accounts/permissions.py` |
| User Registration/Login | Custom User model with email login | `accounts/models.py` |
| Password Hashing | Django PBKDF2 with SHA256 | Built-in |
| CRUD APIs | Task ViewSet with filters | `tasks/views.py` |
| API Versioning | `/api/v1/` prefix | `config/urls.py` |
| Input Validation | DRF Serializers | `*/serializers.py` |
| Error Handling | Custom exception handler | `config/exceptions.py` |
| Swagger Documentation | drf-yasg | `config/urls.py` |
| Logging | Server logs | `logs/server_sample.log` |

---

## 2. Architecture Design

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Vanilla JS)  │  Postman  │  Swagger UI           │
└────────────────────────────────────────────────────────────-┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  Django REST Framework                                       │
│  ├── Authentication (JWT)                                    │
│  ├── Permissions (RBAC)                                      │
│  ├── Serializers (Validation)                                │
│  └── Views (Business Logic)                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL Database                                         │
│  ├── User Model (accounts)                                   │
│  └── Task Model (tasks)                                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Project Structure

```
backend/
├── config/                 # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # Root URL routing
│   ├── exceptions.py      # Custom exception handler
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
│
├── accounts/              # Authentication module
│   ├── models.py          # Custom User model
│   ├── serializers.py     # Auth serializers
│   ├── views.py           # Auth views (login, register, etc.)
│   ├── urls.py            # Auth URL patterns
│   ├── permissions.py     # Custom permission classes
│   └── admin.py           # Django admin config
│
├── tasks/                 # Task management module
│   ├── models.py          # Task model
│   ├── serializers.py     # Task serializers
│   ├── views.py           # Task CRUD views
│   ├── urls.py            # Task URL patterns
│   └── admin.py           # Django admin config
│
├── logs/                  # Server logs
│   └── server_sample.log  # Sample API logs
│
├── manage.py              # Django CLI
├── requirements.txt       # Python dependencies
└── .env.example           # Environment template
```

---

## 3. Authentication System

### 3.1 JWT Token Flow

```
┌──────────┐     POST /login/      ┌──────────┐
│  Client  │ ──────────────────▶   │  Server  │
│          │  {email, password}    │          │
└──────────┘                       └──────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │ Validate User   │
                              │ Generate Tokens │
                              └─────────────────┘
                                        │
                                        ▼
┌──────────┐    {access, refresh}   ┌──────────┐
│  Client  │ ◀──────────────────    │  Server  │
│          │                        │          │
└──────────┘                        └──────────┘
      │
      │ Store tokens in localStorage
      ▼
┌──────────┐   Authorization: Bearer <token>   ┌──────────┐
│  Client  │ ─────────────────────────────▶    │  Server  │
│          │       GET /tasks/                 │          │
└──────────┘                                   └──────────┘
```

### 3.2 Token Configuration

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### 3.3 Custom Token Claims

Tokens include additional user information:

```python
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role
        return token
```

---

## 4. Role-Based Access Control

### 4.1 User Roles

| Role | Permissions |
|------|-------------|
| `user` | CRUD own tasks, view profile |
| `admin` | Full access to all users and tasks |

### 4.2 Permission Classes

```python
# accounts/permissions.py

class IsAdminUser(BasePermission):
    """Only admin users can access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsOwnerOrAdmin(BasePermission):
    """Owner or admin can access"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.owner == request.user
```

### 4.3 Access Control Matrix

| Endpoint | User | Admin |
|----------|------|-------|
| `GET /tasks/` | Own tasks only | All tasks |
| `POST /tasks/` | ✅ | ✅ |
| `PUT /tasks/{id}/` | Own only | Any |
| `DELETE /tasks/{id}/` | Own only | Any |
| `GET /admin/users/` | ❌ | ✅ |
| `DELETE /admin/users/{id}/` | ❌ | ✅ |

---

## 5. API Design & Versioning

### 5.1 URL Structure

```
/api/v1/
├── auth/
│   ├── register/          POST - Register new user
│   ├── login/             POST - Get JWT tokens
│   ├── logout/            POST - Blacklist token
│   ├── refresh/           POST - Refresh access token
│   ├── profile/           GET/PUT - User profile
│   ├── change-password/   PUT - Change password
│   └── admin/
│       └── users/         GET/PUT/DELETE - Admin user management
│
└── tasks/
    ├── /                  GET/POST - List/Create tasks
    ├── {id}/              GET/PUT/DELETE - Task detail
    ├── stats/             GET - Task statistics
    └── admin/
        ├── all/           GET - All tasks (admin)
        └── {id}/delete/   DELETE - Delete any task (admin)
```

### 5.2 Response Format

**Success Response:**
```json
{
    "success": true,
    "message": "Task created successfully",
    "data": {
        "id": 1,
        "title": "Complete project",
        "status": "pending"
    }
}
```

**Error Response:**
```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "title": ["This field is required."],
        "priority": ["Invalid choice."]
    }
}
```

### 5.3 HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (Delete) |
| 400 | Validation Error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

## 6. Database Design

### 6.1 Entity Relationship Diagram

```
┌─────────────────────┐         ┌─────────────────────┐
│       User          │         │       Task          │
├─────────────────────┤         ├─────────────────────┤
│ PK  id              │◄────────│ FK  owner_id        │
│     email (unique)  │    1:N  │ PK  id              │
│     username        │         │     title           │
│     password (hash) │         │     description     │
│     role            │         │     status          │
│     first_name      │         │     priority        │
│     last_name       │         │     due_date        │
│     created_at      │         │     created_at      │
│     updated_at      │         │     updated_at      │
└─────────────────────┘         └─────────────────────┘
```

### 6.2 Model Definitions

**User Model:**
```python
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [('user', 'User'), ('admin', 'Admin')]
    
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    # ... other fields
    
    USERNAME_FIELD = 'email'  # Login with email
```

**Task Model:**
```python
class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(choices=PRIORITY_CHOICES, default='medium')
    # ... other fields
```

---

## 7. Error Handling

### 7.1 Custom Exception Handler

```python
# config/exceptions.py

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response = {
            'success': False,
            'message': 'An error occurred',
            'errors': response.data
        }
        
        if isinstance(exc, AuthenticationFailed):
            custom_response['message'] = 'Authentication failed'
        elif isinstance(exc, PermissionDenied):
            custom_response['message'] = 'Permission denied'
        elif isinstance(exc, NotFound):
            custom_response['message'] = 'Resource not found'
            
        response.data = custom_response
    
    return response
```

### 7.2 Validation Errors

Serializer validation provides detailed error messages:

```json
{
    "success": false,
    "message": "Validation failed",
    "errors": {
        "email": ["Enter a valid email address."],
        "password": ["This field may not be blank."],
        "username": ["A user with that username already exists."]
    }
}
```

---

## 8. Security Implementation

### 8.1 Password Security

- **Algorithm:** PBKDF2 with SHA256
- **Iterations:** 390,000 (Django default)
- **Salt:** Random per password

```python
# Password validation in settings.py
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
```

### 8.2 JWT Security

| Feature | Implementation |
|---------|----------------|
| Token Expiry | Access: 60 min, Refresh: 7 days |
| Token Rotation | New refresh token on each refresh |
| Blacklisting | Used tokens are blacklisted |
| Minimal Claims | Only user_id, email, role in token |

### 8.3 Input Validation

- All inputs validated through DRF serializers
- Email format validation
- Username alphanumeric validation
- SQL injection protection via ORM
- XSS protection via Django templating

### 8.4 CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
]
```

---

## 9. Scalability Considerations

### 9.1 Horizontal Scaling Architecture

```
                    ┌───────────────┐
                    │ Load Balancer │
                    │   (Nginx)     │
                    └───────┬───────┘
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Django 1   │  │  Django 2   │  │  Django 3   │
    │  (Gunicorn) │  │  (Gunicorn) │  │  (Gunicorn) │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           └────────────────┼────────────────┘
                    ┌───────┴───────┐
                    │     Redis     │
                    │   (Cache)     │
                    └───────┬───────┘
                    ┌───────┴───────┐
                    │  PostgreSQL   │
                    │   (Primary)   │
                    └───────────────┘
```

### 9.2 Caching Strategy

```python
# Redis caching for frequently accessed data
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# View-level caching
@cache_page(60 * 15)  # Cache for 15 minutes
def task_list(request):
    ...
```

### 9.3 Database Optimization

- **Connection Pooling:** Use `django-db-geventpool`
- **Indexes:** On frequently queried fields (status, priority, owner)
- **Read Replicas:** For read-heavy operations
- **Query Optimization:** Use `select_related` and `prefetch_related`

### 9.4 Future Microservices Architecture

```
┌─────────────────────────────────────────────┐
│              API Gateway                     │
│            (Kong / Nginx)                    │
└─────────────────────────────────────────────┘
         │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  Auth   │    │  Tasks  │    │  Users  │
    │ Service │    │ Service │    │ Service │
    └────┬────┘    └────┬────┘    └────┬────┘
         │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │Auth DB  │    │Tasks DB │    │Users DB │
    └─────────┘    └─────────┘    └─────────┘
```

---

## 10. Testing Strategy

### 10.1 Test Categories

| Type | Purpose | Tools |
|------|---------|-------|
| Unit Tests | Test individual functions | pytest, Django TestCase |
| Integration Tests | Test API endpoints | DRF APIClient |
| Manual Testing | Interactive testing | Swagger UI, Postman |

### 10.2 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test tasks

# Run with coverage
coverage run manage.py test
coverage report
```

### 10.3 Manual Testing with Postman

Import the included `postman_collection.json` for pre-configured API tests.

---

## 11. Deployment Guide

### 11.1 Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Configure allowed hosts
- [ ] Set up static file serving
- [ ] Configure logging
- [ ] Set up monitoring

### 11.2 Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 11.3 Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/primetask
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=primetask_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
  
  redis:
    image: redis:alpine
```

### 11.4 Recommended Production Stack

| Component | Technology |
|-----------|------------|
| Web Server | Nginx |
| Application Server | Gunicorn |
| Database | PostgreSQL |
| Cache | Redis |
| Task Queue | Celery |
| Monitoring | Prometheus + Grafana |
| Container | Docker + Kubernetes |

---

## 📞 Contact

**Guhan S**  
📧 Email: guhan0003@gmail.com  
💼 LinkedIn: https://www.linkedin.com/in/guhan0003/  
🐙 GitHub: https://github.com/Guhan0003

---

*This documentation was created as part of the Backend Developer Internship assignment for Primetrade.ai.*
