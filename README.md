# FastAPI → Django Migration Notes

## Overview
This document summarizes the changes made when migrating the To-Do List backend from FastAPI + SQLAlchemy to Django + Django REST Framework.

---

## Project Structure

### Before (FastAPI)
```
to-do-list-3.0/
  backend/
    auth.py          ← JWT logic
    config.py        ← environment variables
    database.py      ← SQLAlchemy engine + session
    models.py        ← SQLAlchemy models
    serializer.py    ← Pydantic schemas
  main.py            ← FastAPI app + all routes
  alembic/           ← database migrations
  todos.db           ← SQLite database
  frontend/
```

### After (Django)
```
to-do-list-3.0/
  backend/
    accounts/        ← app: handles user registration
    config/          ← project config (settings, urls, wsgi)
    todos/           ← app: handles tasks and categories
    manage.py
    db.sqlite3
  frontend/
```

---

## 1. Dependencies

### Removed
```
fastapi
uvicorn
sqlalchemy
alembic
pydantic
python-jose
passlib
python-multipart
```

### Added
```
django
djangorestframework
djangorestframework-simplejwt
django-cors-headers
```

---

## 2. Settings (`config/settings.py`)

Replaced `config.py` and `database.py`. Key additions:

```python
INSTALLED_APPS = [
    'accounts.apps.AccountsConfig',
    'todos.apps.TodosConfig',
    'rest_framework',
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be first
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

USE_TZ = True
TIME_ZONE = 'Asia/Dhaka'
```

---

## 3. Models (`todos/models.py`)

Replaced SQLAlchemy models with Django ORM models.

| SQLAlchemy | Django ORM |
|---|---|
| `class User(Base)` | ❌ deleted — uses Django's built-in `User` |
| `Column(Integer, primary_key=True)` | `models.AutoField` (automatic) |
| `Column(String)` | `models.CharField(max_length=...)` |
| `Column(Boolean)` | `models.BooleanField()` |
| `Column(DateTime)` | `models.DateTimeField()` |
| `ForeignKey("users.id")` | `models.ForeignKey(User, on_delete=models.CASCADE)` |
| `relationship(...)` | `models.ForeignKey(...)` with `related_name` |
| `category = Column(String)` | `category = models.ForeignKey(Category, ...)` |
| `Base.metadata.create_all()` | `python manage.py migrate` |

---

## 4. Serializers (`todos/serializers.py`)

Replaced Pydantic schemas with DRF serializers.

| Pydantic | DRF Serializer |
|---|---|
| `class UserCreate(BaseModel)` | `UserCreateSerializer(ModelSerializer)` |
| `class UserPublic(BaseModel)` | `UserPublicSerializer(ModelSerializer)` |
| `class TaskCreate + TaskResponse` | `TodoSerializer(ModelSerializer)` |
| `class Token(BaseModel)` | ❌ deleted — simplejwt handles this |
| `class Config: from_attributes = True` | ❌ not needed |
| manual password handling | `create_user()` auto-hashes password |
| `owner_id: int` | `owner = UserPublicSerializer(read_only=True)` |
| category as plain string | `category = CategorySerializer(read_only=True)` |

---

## 5. Authentication

Entire `auth.py` deleted. Everything replaced by Django + simplejwt.

| `auth.py` function | Django replacement |
|---|---|
| `hash_password()` | `User.objects.create_user()` |
| `verify_password()` | `user.check_password()` |
| `create_access_token()` | simplejwt automatic |
| `authenticate_user()` | `django.contrib.auth.authenticate()` |
| `get_current_user()` | `IsAuthenticated` permission class |
| `get_username_from_header()` | simplejwt middleware |
| `OAuth2PasswordBearer` | simplejwt |
| `SECRET_KEY`, `ALGORITHM` | `settings.py` SIMPLE_JWT config |

---

## 6. Views (`todos/views.py`)

Replaced FastAPI route functions with DRF `@api_view` decorators.

| FastAPI | Django DRF |
|---|---|
| `@app.get("/api/tasks")` | `@api_view(['GET'])` |
| `Depends(get_current_user)` | `request.user` |
| `Depends(get_db)` | ❌ not needed |
| `db.query(Todo).filter(...)` | `Todo.objects.filter(...)` |
| `db.add(task); db.commit()` | `Todo.objects.create(...)` |
| `db.refresh(task)` | ❌ not needed |
| `raise HTTPException(404)` | `return Response(..., status=404)` |
| `Form(...)` parameters | `request.data.get(...)` |

Added `resolve_category()` helper to handle category name → ID resolution since React was sending category names instead of IDs.

Added timezone-aware deadline parsing:
```python
from datetime import datetime, timezone as dt_timezone
datetime.fromisoformat(deadline).replace(tzinfo=dt_timezone.utc)
```

---

## 7. URLs

Replaced single `main.py` router with three URL files.

| FastAPI (`main.py`) | Django |
|---|---|
| `@app.post("/api/login")` | `TokenObtainPairView` in `config/urls.py` |
| `@app.post("/api/register")` | `register` view in `accounts/urls.py` |
| `@app.get("/api/tasks")` | `todos/urls.py` |
| no trailing slashes | trailing slashes required |

**`config/urls.py`** — root router:
```python
path('api/auth/register/', register)
path('api/auth/login/', TokenObtainPairView)
path('api/auth/refresh/', TokenRefreshView)
path('api/', include('todos.urls'))
```

---

## 8. Database

| FastAPI | Django |
|---|---|
| `database.py` SQLAlchemy engine | ❌ deleted |
| `get_db()` dependency injection | ❌ deleted |
| `alembic` migrations | `python manage.py makemigrations` |
| `Base.metadata.create_all()` | `python manage.py migrate` |
| `todos.db` | `db.sqlite3` (auto-created) |

---

## 9. Frontend `api.js` Changes

| Before (FastAPI) | After (Django) |
|---|---|
| `BASE = ""` | `BASE = "http://localhost:8000"` |
| `/api/login` | `/api/auth/login/` |
| `/api/register` | `/api/auth/register/` |
| `data.access_token` | `data.access` |
| `/api/tasks` POST | `/api/tasks/add/` |
| `/api/tasks/${id}` DELETE | `/api/tasks/${id}/delete/` |
| `/api/categories` POST | `/api/categories/add/` |
| no trailing slashes | trailing slashes on all URLs |
| register returns token | register calls login() separately |
| raw datetime string | `toUTCString()` converts to UTC ISO |

---

## 10. Frontend React Changes

### `index.jsx`
- `task.category` → `task.category?.name` everywhere
- `task.category?.icon` for displaying category icon
- Username fetched from `/api/me/` instead of decoded from JWT
- Date comparisons use UTC methods (`getUTCDate`, `getUTCMonth`, `getUTCFullYear`)
- Deadline display uses `toLocaleString('en-BD', { timeZone: 'Asia/Dhaka' })`

### `category-panel.jsx`
- `t.category === c.name` → `t.category?.name === c.name`
- Uncategorized count uses `t.category?.name`

### `calendar.jsx`
- All date methods changed to UTC (`getUTCDate`, `getUTCMonth`, `getUTCFullYear`)
- `today` calculated with `getUTCDate()`
- Removed duplicate `forEach` that was adding tasks to `deadlineMap` twice

### `package.json`
- `name` updated to `to-do-list-3.0`
- `start:backend` changed from `uvicorn main:app --reload` to `python manage.py runserver`

---

## 11. Common Gotchas

- **Trailing slashes** — Django requires them, FastAPI doesn't
- **Token key** — simplejwt returns `access` not `access_token`
- **Category as object** — Django returns `{id, name, icon}` not a plain string
- **UTC deadlines** — Django stores UTC, frontend must convert for display
- **`accounts` app name** — `apps.py` must say `name = 'accounts'` not `'account'`
- **`CorsMiddleware`** — must be the very first middleware
- **Form parsing** — DRF needs `FormParser` in `DEFAULT_PARSER_CLASSES` to accept `application/x-www-form-urlencoded`