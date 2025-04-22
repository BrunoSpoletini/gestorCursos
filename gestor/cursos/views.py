from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Course, Enrollment, Grade

# Local imports
from .permissions import IsAdmin, IsInstructor, IsStudent
from .serializers import (
    CourseSerializer,
    EnrollmentSerializer,
    GradesSerializer,
    UserSerializer,
)

User = get_user_model()

@extend_schema(
    tags=["Users"],
)
class UserView(generics.ListAPIView):
    """
    List all users
    """
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]
    http_method_names = ["get"]

@extend_schema(
    tags=["Users"],
)
class UserRegisterView(generics.CreateAPIView):
    """
    Register a user with a role
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(
    tags=["Course"],
)
class CourseViewSet(viewsets.ModelViewSet):
    """
    Allows instructors to create, list and look for courses
    """
    
    queryset = Course.objects.all().order_by("-id")
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = [IsAdmin | IsInstructor]
        elif self.action in ["list", "retrieve"]:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()


@extend_schema(
    tags=["Enrollment"],
)
class EnrollmentView(generics.CreateAPIView):
    """
    Allows students to enroll in a course
    """

    queryset = Course.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

@extend_schema(
    tags=["Enrollment"],
)
class EnrollmentsUserView(generics.ListAPIView):
    """
    Returns a list of enrollments for the authenticated student
    """

    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).order_by("-id")


@extend_schema(
    tags=["Grade"],
)
class GradeView(generics.CreateAPIView):
    """
    Allows instructors to create a new grade
    """

    queryset = Grade.objects.all().order_by("-id")
    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsInstructor]

@extend_schema(
    tags=["Grade"],
)
class GradeInstructorView(generics.ListAPIView):
    """
    Returns a list of grades for a specific course created by the instructor
    """

    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsInstructor]

    def get(self, request, course_id=None):

        course = get_object_or_404(Course, id=course_id)
        
        # # Check instructor permission
        if course.created_by != request.user and not request.user.is_admin:
            return Response({"detail": "You don't have permission to view these grades"}, status=403)
        
        # # Get grades for this course
        grades = Grade.objects.filter(enrollment__course=course)
        serializer = GradesSerializer(grades, many=True)
        return Response(serializer.data)

@extend_schema(
    tags=["Grade"],
)
class GradeStudentView(generics.ListAPIView):
    """
    Returns a list of grades for the authenticated student
    """

    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def get_queryset(self):
        user = self.request.user
        return Grade.objects.filter(enrollment__user=user).order_by("-id")

@extend_schema(
    tags=["Users"],
    description="Obtains a JWT token pair (access and refresh tokens) by providing username and password.",
)
class CustomTokenObtainPairView(TokenObtainPairView):
    pass