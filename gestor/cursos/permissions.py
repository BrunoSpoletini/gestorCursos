from django.contrib.auth import get_user_model

from rest_framework.permissions import BasePermission

User = get_user_model()

class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsInstructor(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.Roles.INSTRUCTOR
            
class IsStudent(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.Roles.STUDENT

class IsAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == User.Roles.ADMIN    

