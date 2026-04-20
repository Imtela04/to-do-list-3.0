from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
from .models import Todo, Category
from .serializers import TodoSerializer, CategorySerializer
from datetime import datetime, timezone as dt_timezone  # ← add timezone as dt_timezone
from django.utils import timezone

DEFAULT_CATEGORIES = [
    {"name": "work",      "icon": "💼"},
    {"name": "personal",  "icon": "🏠"},
    {"name": "health",    "icon": "💪"},
    {"name": "finance",   "icon": "💰"},
    {"name": "education", "icon": "📚"},
    {"name": "other",     "icon": "📌"},
]


# replaces GET /api/me
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({"username": request.user.username})


# replaces GET /api/tasks
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    todos = Todo.objects.filter(owner=request.user)
    serializer = TodoSerializer(todos, many=True)
    return Response(serializer.data)

def resolve_category(category_value, user):
    """Helper to resolve category name or id to a category id"""
    if not category_value:
        return None
    try:
        return int(category_value)
    except (ValueError, TypeError):
        cat = Category.objects.filter(name=category_value, owner=user).first()
        return cat.id if cat else None
    
# replaces POST /api/tasks
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_task(request):
    title = request.data.get('title', '').strip()
    description = request.data.get('description', None)
    deadline = request.data.get('deadline', None)
    category_id = resolve_category(request.data.get('category'), request.user)

    if Todo.objects.filter(title=title, owner=request.user).exists():
        return Response(
            {"detail": "Task with this title already exists"},
            status=status.HTTP_409_CONFLICT
        )

    task = Todo.objects.create(
        title=title,
        owner=request.user,
        description=description or None,
        deadline=datetime.fromisoformat(deadline).replace(tzinfo=dt_timezone.utc) if deadline else None,
        category_id=category_id,
    )

    return Response(TodoSerializer(task).data, status=status.HTTP_201_CREATED)


# replaces DELETE /api/tasks/{task_id}
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    task = Todo.objects.filter(id=task_id, owner=request.user).first()
    if not task:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    task.delete()
    return Response({"ok": True})


# replaces PATCH /api/tasks/{task_id}/title
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_title(request, task_id):
    task = Todo.objects.filter(id=task_id, owner=request.user).first()
    if not task:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    task.title = request.data.get('title', task.title)
    task.save()
    return Response(TodoSerializer(task).data)


# replaces PATCH /api/tasks/{task_id}/description
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_description(request, task_id):
    task = Todo.objects.filter(id=task_id, owner=request.user).first()
    if not task:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    task.description = request.data.get('description', task.description)
    task.save()
    return Response(TodoSerializer(task).data)


# replaces PATCH /api/tasks/{task_id}/deadline
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_deadline(request, task_id):
    task = Todo.objects.filter(id=task_id, owner=request.user).first()
    if not task:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    deadline = request.data.get('deadline')
    task.deadline = datetime.fromisoformat(deadline).replace(tzinfo=dt_timezone.utc) if deadline else None
    task.save()
    return Response(TodoSerializer(task).data)


# replaces PATCH /api/tasks/{task_id}/category
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_task_category(request, task_id):
    task = Todo.objects.filter(id=task_id, owner=request.user).first()
    if not task:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    task.category_id = resolve_category(request.data.get('category'), request.user)
    task.save()
    return Response(TodoSerializer(task).data)

# replaces PATCH /api/tasks/{task_id}/toggle
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def toggle_task(request, task_id):
    task = Todo.objects.filter(id=task_id, owner=request.user).first()
    if not task:
        return Response({"detail": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
    task.completed = not task.completed
    task.save()
    return Response(TodoSerializer(task).data)


# replaces GET /api/categories
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_categories(request):
    categories = Category.objects.filter(owner=request.user)
    return Response(CategorySerializer(categories, many=True).data)


# replaces POST /api/categories
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_category(request):
    name = request.data.get('name', '').strip()
    icon = request.data.get('icon', '🏷️')
    cat = Category.objects.create(name=name, icon=icon, owner=request.user)
    return Response(CategorySerializer(cat).data, status=status.HTTP_201_CREATED)


# replaces PATCH /api/categories/{cat_id}
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_category(request, cat_id):
    cat = Category.objects.filter(id=cat_id, owner=request.user).first()
    if not cat:
        return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    cat.name = request.data.get('name', cat.name)
    icon = request.data.get('icon')
    if icon:
        cat.icon = icon
    cat.save()
    return Response(CategorySerializer(cat).data)


# replaces DELETE /api/categories/{cat_id}
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category(request, cat_id):
    cat = Category.objects.filter(id=cat_id, owner=request.user).first()
    if not cat:
        return Response({"detail": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    cat.delete()
    return Response({"ok": True})