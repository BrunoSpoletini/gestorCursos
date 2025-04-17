from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
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


# User Endpoints
class UserView(generics.ListAPIView):
    """
    GET /api/users/ - Admin
    Lista de todos los usuarios
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]


class UserRegisterView(generics.CreateAPIView):
    """ "
    POST /api/register/ - Public
    Registro de usuario con rol
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


# Course Endpoints
class CourseViewSet(viewsets.ModelViewSet):
    """
    GET /api/courses/ - Public
    Returns a list of all courses

    GET /api/courses/<int:pk>/ - Public
    Returns details of a specific course

    POST /api/courses/ - Instructor
    Allows instructors to create a new course
    """

    queryset = Course.objects.all().order_by("-id")
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["create"]:
            self.permission_classes = [IsAdmin | IsInstructor]
        elif self.action in ["list", "retrieve"]:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()


# Enrollment Endpoints
class EnrollmentView(generics.CreateAPIView):
    """
    POST /api/enroll/ - Student
    Allows students to enroll in a course
    """

    queryset = Course.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]


class EnrollmentsUserView(generics.ListAPIView):
    """
    GET /api/my-enrollments/ - Student
    Returns a list of enrollments for the authenticated student
    """

    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user).order_by("-id")


# Grade Endpoints
class GradeInstructorViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/grades/ - Instructor
    Allows instructors to create a new grade
    """

    queryset = Grade.objects.all().order_by("-id")
    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsInstructor]

    @action(detail=False, methods=["GET"], url_path="course/(?P<course_id>[^/.]+)")
    def grades_by_course(self, request, course_id=None):
        """
        GET /api/grades/course/<int:pk>/ - Instructor
        Returns a list of grades for a specific course created by the instructor
        """
        course = get_object_or_404(Course, pk=course_id)
        # Check if the instructor is the creator of the course
        if course.created_by != request.user:
            return Response(
                {"detail": "You do not have permission to view these grades."},
                status=403,
            )

        # Retrieve grades for
        grades = Grade.objects.filter(enrollment__course=course)
        serializer = self.get_serializer(grades, many=True)
        return Response(serializer.data)


class GradeStudentView(generics.ListAPIView):
    """
    GET /api/my-grades/ - Student
    Returns a list of grades for the authenticated student
    """

    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def get_queryset(self):
        user = self.request.user
        return Grade.objects.filter(enrollment__user=user).order_by("-id")
