# 🚀 PrimeTask API

**Backend Developer Internship Assignment - Primetrade.ai**

A **Scalable REST API** with Authentication & Role-Based Access Control, built with Django REST Framework.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [API Documentation](#api-documentation)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Security Practices](#security-practices)
- [Scalability Notes](#scalability-notes)
- [Testing](#testing)

---

## 🎯 Overview

PrimeTask is a task management system that demonstrates production-ready backend development practices including:

- **JWT Authentication** with secure token handling
- **Role-Based Access Control** (User vs Admin)
- **RESTful API Design** with proper versioning
- **Input Validation** and comprehensive error handling
- **Swagger/OpenAPI Documentation**
- **Clean, scalable project architecture**

---

## ✨ Features

### Backend (Primary Focus)
- ✅ User registration & login with password hashing (bcrypt via Django)
- ✅ JWT authentication with access/refresh tokens
- ✅ Role-based access control (User & Admin roles)
- ✅ Complete CRUD APIs for Task management
- ✅ API versioning (`/api/v1/`)
- ✅ Comprehensive error handling with custom exception handler
- ✅ Input validation using Django REST Framework serializers
- ✅ Swagger/OpenAPI documentation at `/swagger/`
- ✅ PostgreSQL/SQLite database support
- ✅ Custom permission classes

### Frontend (Supportive)
- ✅ Clean, responsive UI built with Vanilla JS
- ✅ User registration and login forms
- ✅ Protected dashboard (JWT required)
- ✅ Task CRUD operations with filtering
- ✅ Admin panel for user/task management
- ✅ Error/success toast notifications
- ✅ Token refresh mechanism

### Security
- ✅ Password hashing with Django's PBKDF2 algorithm
- ✅ JWT tokens with configurable expiry
- ✅ Token blacklisting on logout
- ✅ Input sanitization via serializers
- ✅ CORS configuration
- ✅ Role-based permissions

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | Django 4.2 |
| REST API | Django REST Framework 3.14 |
| Authentication | SimpleJWT |
| Database | PostgreSQL 13+ |
| API Documentation | drf-yasg (Swagger) |
| Frontend | Vanilla JavaScript, HTML5, CSS3 |

---

## 📁 Project Structure

```
primetrade/
├── backend/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # Django settings
│   │   ├── urls.py          # Main URL routing
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── exceptions.py    # Custom exception handler
│   │
│   ├── accounts/
│   │   ├── __init__.py
│   │   ├── models.py        # Custom User model
│   │   ├── serializers.py   # Auth serializers
│   │   ├── views.py         # Auth views
│   │   ├── urls.py          # Auth URLs
│   │   ├── permissions.py   # Custom permissions
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── models.py        # Task model
│   │   ├── serializers.py   # Task serializers
│   │   ├── views.py         # Task views
│   │   ├── urls.py          # Task URLs
│   │   ├── admin.py
│   │   └── apps.py
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
└── README.md
```

---

## 🗄 Database Schema

### User Model
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key (auto) |
| email | Email | Unique, used for login |
| username | String | Unique, alphanumeric |
| password | String | Hashed password |
| role | Enum | `user` or `admin` |
| first_name | String | Optional |
| last_name | String | Optional |
| created_at | DateTime | Auto timestamp |
| updated_at | DateTime | Auto timestamp |

### Task Model
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key (auto) |
| title | String | Task title (max 200) |
| description | Text | Optional description |
| status | Enum | `pending`, `in_progress`, `completed`, `cancelled` |
| priority | Enum | `low`, `medium`, `high` |
| due_date | DateTime | Optional due date |
| owner | ForeignKey | Reference to User |
| created_at | DateTime | Auto timestamp |
| updated_at | DateTime | Auto timestamp |

### Entity Relationship

```
┌─────────────┐       ┌──────────────┐
│    User     │       │     Task     │
├─────────────┤       ├──────────────┤
│ id (PK)     │◄──────│ owner (FK)   │
│ email       │   1:N │ id (PK)      │
│ username    │       │ title        │
│ password    │       │ description  │
│ role        │       │ status       │
│ created_at  │       │ priority     │
│ updated_at  │       │ due_date     │
└─────────────┘       │ created_at   │
                      │ updated_at   │
                      └──────────────┘
```

---

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8000/swagger/
- **ReDoc**: http://127.0.0.1:8000/redoc/
- **OpenAPI JSON**: http://127.0.0.1:8000/swagger.json

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- pip (Python package manager)
- PostgreSQL 13+ (installed and running)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd primetrade
```

### 2. Create Virtual Environment
```bash
# Windows
cd backend
python -m venv venv
venv\Scripts\activate

# macOS/Linux
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env file with your PostgreSQL settings
```

### 5. Setup PostgreSQL Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE primetask_db;

# Exit psql
\q
```

Or using pgAdmin, create a new database named `primetask_db`.

### 6. Initialize Database
```bash
# Create migrations
python manage.py makemigrations accounts
python manage.py makemigrations tasks

# Apply migrations
python manage.py migrate

# Create superuser (admin)
python manage.py createsuperuser
```

### 7. Create Admin User via Shell (Alternative)
```bash
python manage.py shell
```
```python
from accounts.models import User
User.objects.create_superuser(
    email='admin@example.com',
    username='admin',
    password='admin123',
    role='admin'
)
exit()
```

---

## ▶️ Running the Application

### Start Backend Server
```bash
cd backend
python manage.py runserver
```
Backend will be available at: http://127.0.0.1:8000

### Access Frontend
1. Open `frontend/index.html` in your browser
2. Or use Live Server extension in VS Code

### Quick Test URLs
- API Root: http://127.0.0.1:8000/
- Swagger Docs: http://127.0.0.1:8000/swagger/
- Admin Panel: http://127.0.0.1:8000/admin/

---

## 📡 API Endpoints

### Authentication Endpoints (`/api/v1/auth/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/register/` | Register new user | No |
| POST | `/login/` | Login & get tokens | No |
| POST | `/refresh/` | Refresh access token | No |
| POST | `/logout/` | Logout & blacklist token | Yes |
| GET | `/profile/` | Get current user profile | Yes |
| PUT/PATCH | `/profile/` | Update profile | Yes |
| PUT | `/change-password/` | Change password | Yes |

### Admin User Endpoints (`/api/v1/auth/admin/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/` | List all users | Admin |
| GET | `/users/{id}/` | Get user details | Admin |
| PUT/PATCH | `/users/{id}/` | Update user | Admin |
| DELETE | `/users/{id}/` | Delete user | Admin |

### Task Endpoints (`/api/v1/tasks/`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | List tasks (filtered by role) | Yes |
| POST | `/` | Create new task | Yes |
| GET | `/{id}/` | Get task details | Yes (Owner/Admin) |
| PUT/PATCH | `/{id}/` | Update task | Yes (Owner/Admin) |
| DELETE | `/{id}/` | Delete task | Yes (Owner/Admin) |
| GET | `/stats/` | Get task statistics | Yes |

### Admin Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/all/` | List all tasks | Admin |
| DELETE | `/admin/{id}/delete/` | Delete any task | Admin |

### Example API Requests

#### Register User
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

#### Login
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

#### Create Task (with JWT)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "title": "Complete project",
    "description": "Finish the PrimeTask API",
    "priority": "high"
  }'
```

---

## 🔐 Security Practices

### Password Security
- Passwords are hashed using Django's PBKDF2 algorithm with SHA256
- Password validation enforces minimum length (8 chars) and complexity
- Passwords are never stored or transmitted in plain text

### JWT Token Security
- **Access Token**: Short-lived (60 minutes by default)
- **Refresh Token**: Longer-lived (7 days by default)
- Tokens are rotated on refresh
- Used tokens are blacklisted
- Tokens contain minimal claims (user_id, role)

### Input Validation
- All inputs are validated through DRF serializers
- Email format validation
- Username alphanumeric validation
- SQL injection protection via ORM
- XSS protection via output encoding

### CORS
- CORS is configured to allow frontend communication
- Should be restricted to specific origins in production

---

## 📈 Scalability Notes

This project is designed with scalability in mind. Here are strategies for scaling:

### 1. Horizontal Scaling
```
                    ┌───────────────┐
                    │ Load Balancer │
                    └───────┬───────┘
           ┌────────────────┼────────────────┐
           ▼                ▼                ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │  Django 1   │  │  Django 2   │  │  Django 3   │
    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
           └────────────────┼────────────────┘
                    ┌───────┴───────┐
                    │   PostgreSQL  │
                    │   (Primary)   │
                    └───────────────┘
```

### 2. Caching Strategy (Redis)
```python
# Example Redis caching implementation
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache decorators for views
@cache_page(60 * 15)  # Cache for 15 minutes
def task_list(request):
    ...
```

### 3. Database Optimization
- Use database connection pooling
- Add indexes on frequently queried fields
- Implement read replicas for read-heavy operations
- Consider database sharding for large datasets

### 4. Microservices Architecture (Future)
```
┌─────────────────────────────────────────────┐
│                 API Gateway                  │
└─────────────────────────────────────────────┘
         │              │              │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │  Auth   │    │  Tasks  │    │  Users  │
    │ Service │    │ Service │    │ Service │
    └─────────┘    └─────────┘    └─────────┘
```

### 5. Docker Deployment
```dockerfile
# Example Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### 6. Recommended Production Stack
- **Web Server**: Nginx + Gunicorn
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis for session and query caching
- **Queue**: Celery for async tasks
- **Monitoring**: Prometheus + Grafana
- **Container**: Docker + Kubernetes

---

## 🧪 Testing

### Run Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test tasks
```

### Manual Testing with Swagger
1. Navigate to http://127.0.0.1:8000/swagger/
2. Try out endpoints directly from the browser
3. Use the "Authorize" button to add JWT token

---

## 📝 License

This project is created for the Primetrade.ai Backend Developer Internship assignment.

---

## 👤 Author

**Guhan S**

Created as part of the Backend Developer (Intern) assignment for Primetrade.ai.

- 📧 Email: guhan0003@gmail.com
- 💼 LinkedIn: https://www.linkedin.com/in/guhan0003/
- 🐙 GitHub: https://github.com/Guhan0003

---

## 🙏 Acknowledgments

- Django REST Framework documentation
- SimpleJWT for JWT authentication
- Primetrade.ai for the opportunity
