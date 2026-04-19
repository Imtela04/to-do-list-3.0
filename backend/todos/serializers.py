from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Todo, Category

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username', 'password']
    def create(self, validated_data):
        # create_user handles password hashing automatically
        # replaces manually hashing password in auth.py
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

# class UserCreate(BaseModel):
#     username: str
#     # email: str
#     password: str

#  class UserPublic(BaseModel):
class UserPublicSerializer(serializers.ModelSerializer):
    # username: str
    # class Config:
    class Meta:
        # from_attributes = True
        model = User
        fields = ['username']
# replaces TaskCreate + TaskResponse combined
class TodoSerializer(serializers.ModelSerializer):
    owner = UserPublicSerializer(read_only=True)  # replaces owner_id

    class Meta:
        model = Todo
        fields = ['id', 'title', 'completed', 'description', 'deadline', 'category', 'owner']
        read_only_fields = ['id', 'owner']

# class TaskCreate(BaseModel):
#     title: str
#     completed: bool = False
# class TaskResponse(BaseModel):
#     id: int
#     title: str
#     completed: bool
#     owner_id: int

#     class Config:
#         from_attributes = True

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']
        read_only_fields = ['id']


# ❌ not needed — simplejwt handles this automatically
# class Token(BaseModel):
#     access_token: str
#     token_type: str = "bearer"