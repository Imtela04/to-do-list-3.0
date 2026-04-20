Here's a conceptual breakdown of every change and why it was made:

---

## 1. The App Structure

In FastAPI you had one flat folder with loose files. Django enforces a **modular app structure**:

```
backend/
  config/    ← project brain
  accounts/  ← one feature = one app
  todos/     ← one feature = one app
```

**Why?** Django apps are designed to be self-contained and reusable. The `todos` app only knows about todos. The `accounts` app only knows about users. They don't depend on each other (except `todos` importing Django's built-in `User`). This makes your code easier to maintain and scale.

📖 Read: https://docs.djangoproject.com/en/5.1/intro/reusable-apps/

---

## 2. Settings Replace `config.py` + `database.py`

In FastAPI you had:
```python
# config.py
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# database.py
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
```

In Django everything lives in one `settings.py`:
```python
SECRET_KEY = "..."
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Why?** Django's philosophy is "batteries included" — the framework manages the database connection for you. You never write `engine`, `SessionLocal`, or `get_db()` again. Django opens and closes database connections automatically per request.

📖 Read: https://docs.djangoproject.com/en/5.1/topics/settings/
📖 Read: https://docs.djangoproject.com/en/5.1/ref/databases/

---

## 3. Django ORM Replaces SQLAlchemy

This is the biggest conceptual shift. In FastAPI you described your database tables like this:

```python
# SQLAlchemy
class Todo(Base):
    __tablename__ = "todos"
    id       = Column(Integer, primary_key=True)
    title    = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
```

In Django you write this instead:
```python
# Django ORM
class Todo(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
```

**Key conceptual differences:**

- **No `__tablename__`** — Django infers the table name from the class name (`todos_todo`)
- **No `Column()`** — replaced by `models.CharField()`, `models.BooleanField()` etc
- **No `ForeignKey("users.id")` string** — you pass the actual model class `ForeignKey(User, ...)`
- **No `Base`** — all models inherit from `models.Model`
- **No `db.add()`, `db.commit()`** — replaced by `todo.save()` or `Todo.objects.create()`
- **No `db.query(Todo).filter(...)`** — replaced by `Todo.objects.filter(...)`

The Django ORM is also more Pythonic — you query like this:
```python
# SQLAlchemy
db.query(Todo).filter(Todo.owner_id == user.id).all()

# Django ORM
Todo.objects.filter(owner=user)
```

📖 Read: https://docs.djangoproject.com/en/5.1/topics/db/models/
📖 Read: https://docs.djangoproject.com/en/5.1/topics/db/queries/

---

## 4. Migrations Replace Alembic

In FastAPI you used Alembic to manage database schema changes:
```bash
alembic revision --autogenerate
alembic upgrade head
```

Django has migrations built in:
```bash
python manage.py makemigrations  # detect model changes
python manage.py migrate         # apply changes to database
```

**Conceptually the same thing** — both tools detect changes to your models and generate SQL to update the database. Django's version is just built-in and simpler to use. Every time you change a model you run both commands.

📖 Read: https://docs.djangoproject.com/en/5.1/topics/migrations/

---

## 5. DRF Serializers Replace Pydantic

In FastAPI, Pydantic validated incoming data and shaped outgoing responses:
```python
class TaskCreate(BaseModel):
    title: str
    completed: bool = False

class TaskResponse(BaseModel):
    id: int
    title: str
    owner_id: int
    class Config:
        from_attributes = True
```

In Django REST Framework, one serializer does both jobs:
```python
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'completed', 'owner']
```

**Key differences:**
- One serializer replaces both `TaskCreate` and `TaskResponse`
- `ModelSerializer` reads directly from your model — no `Config: from_attributes`
- Nested serializers replace plain IDs: `owner = UserPublicSerializer(read_only=True)` returns `{"username": "john"}` instead of just `owner_id: 1`
- `read_only=True` fields are included in responses but ignored on input
- `write_only=True` fields (like `password`) are accepted on input but never returned

📖 Read: https://www.django-rest-framework.org/api-guide/serializers/
📖 Read: https://www.django-rest-framework.org/tutorial/1-serialization/

---

## 6. simplejwt Replaces `auth.py`

Your entire `auth.py` — 80+ lines of JWT logic — was deleted because `djangorestframework-simplejwt` handles everything:

```python
# your old auth.py did all of this manually:
pwd_context = CryptContext(schemes=["bcrypt"])   # password hashing
oauth2_scheme = OAuth2PasswordBearer(...)         # token extraction
create_access_token(...)                          # token generation
jwt.decode(token, SECRET_KEY, ...)               # token validation
get_current_user(token, db)                       # user lookup from token
```

In Django you just configure it in `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

And add two URLs:
```python
path('api/auth/login/', TokenObtainPairView.as_view())
path('api/auth/refresh/', TokenRefreshView.as_view())
```

That's it. simplejwt now intercepts every request, reads the `Authorization: Bearer <token>` header, validates the token, and puts the user in `request.user`. You never write any of that code yourself.

📖 Read: https://django-rest-framework-simplejwt.readthedocs.io/en/latest/

---

## 7. `request.user` Replaces `Depends(get_current_user)`

This is the most visible day-to-day difference. In FastAPI every protected route needed two dependencies:

```python
# FastAPI
def get_tasks(
    current_user: UserPublic = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == current_user.username).first()
    return user.todos
```

In Django both are gone:
```python
# Django
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    todos = Todo.objects.filter(owner=request.user)
    return Response(serializer.data)
```

**Why?** Django's middleware system automatically handles both. By the time your view function runs, `request.user` is already populated with the authenticated user object. The `@permission_classes([IsAuthenticated])` decorator just returns a 401 if no valid token was provided.

📖 Read: https://www.django-rest-framework.org/api-guide/permissions/
📖 Read: https://www.django-rest-framework.org/api-guide/views/#function-based-views

---

## 8. Trailing Slashes

FastAPI doesn't care about trailing slashes. Django requires them by default:

```
# FastAPI
/api/tasks
/api/tasks/1

# Django
/api/tasks/
/api/tasks/1/
```

This is controlled by `APPEND_SLASH = True` in Django settings (it's `True` by default). The reason is that Django was originally built for content websites where `/about` and `/about/` are meaningfully different URLs. It's a convention the framework carries forward.

---

## 9. CORS

In FastAPI you added CORS middleware manually:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

In Django you install `django-cors-headers` and configure it in `settings.py`. The key lesson was that `CorsMiddleware` **must be first** in the `MIDDLEWARE` list because middleware runs top-to-bottom on requests and bottom-to-top on responses. CORS headers need to be added before any other middleware processes the response.

📖 Read: https://github.com/adamchainz/django-cors-headers

---

## 10. UTC and Timezones

This was a subtle bug. When `USE_TZ = True` in Django settings, all datetimes are stored in UTC in the database. Your React frontend sends datetime strings from `<input type="datetime-local">` which are in **local time** (GMT+6 for you), not UTC. So you needed to:

1. Convert to UTC before sending to Django (`toUTCString()` in `api.js`)
2. Convert back to local time when displaying (`toLocaleString('en-BD', { timeZone: 'Asia/Dhaka' })`)
3. Use UTC methods in calendar comparisons (`getUTCDate()` instead of `getDate()`)

This is a universal web development problem — always store UTC, always display local.

📖 Read: https://docs.djangoproject.com/en/5.1/topics/i18n/timezones/

---

## General Django Learning Resources

These are the best places to go deeper in order:

**Official Django tutorial** (you've done this):
https://docs.djangoproject.com/en/5.1/intro/tutorial01/

**Django REST Framework tutorial** (most important next step):
https://www.django-rest-framework.org/tutorial/quickstart/

**Two Scoops of Django** — the definitive best practices book:
https://www.feldroy.com/books/two-scoops-of-django-3-x

**LearnDjango** — best free written tutorials:
https://learndjango.com/

**Django REST Framework full guide:**
https://www.django-rest-framework.org/

**Real Python Django tutorials:**
https://realpython.com/tutorials/django/