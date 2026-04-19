from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=10, default='🏷️')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    def __str__(self):
        return self.name

class Todo(models.Model):
    title = models.CharField(max_length=255) 
    completed = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='todos')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

#2.0 
# from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
# from sqlalchemy.orm import relationship
# from backend.database import Base

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     todos = relationship("Todo", back_populates="owner")
#     categories = relationship("Category", back_populates="owner", cascade="all, delete")
# class Todo(Base):
#     __tablename__ = "todos"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     completed = Column(Boolean, default=False)   # ✅ was String
#     description = Column(String, nullable=True)
#     deadline = Column(DateTime, nullable=True)   # ✅ new
#     category = Column(String, nullable=True)     # ✅ new
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     owner = relationship("User", back_populates="todos")

# class Category(Base):
#     __tablename__ = "categories"
#     id       = Column(Integer, primary_key=True)
#     name     = Column(String, nullable=False)
#     icon     = Column(String, default="🏷️")
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     owner    = relationship("User", back_populates="categories")