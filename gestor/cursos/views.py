from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import mixins, permissions, viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication

# Local imports
from . permissions import IsInstructor, IsStudent, IsAdmin
from . models import Course, Grade, Enrollment
from . serializers import UserSerializer, CourseSerializer, GradesSerializer, EnrollmentSerializer

User = get_user_model()

# User Endpoints
class UserView(generics.ListAPIView):  
    """
    GET /api/users/ - Admin
    Lista de todos los usuarios 
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

class UserRegisterView(generics.CreateAPIView):
    """"
    POST /api/register/ - Public
    Registro de usuario con rol 
    """
    queryset = User.objects.all().order_by('-date_joined')
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
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['create']:
            self.permission_classes = [IsAdmin | IsInstructor]
        elif self.action in ['list', 'retrieve']:
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

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class EnrollmentsUserView(generics.ListAPIView):
    """
    GET /api/my-enrollments/ - Student
    Returns a list of enrollments for the authenticated student
    """
    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)
    
# Grade Endpoints
class GradeInstructorViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    POST /api/grades/ - Instructor
    Allows instructors to create a new grade
    """
    queryset = Grade.objects.all()
    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsInstructor]

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def grades_by_course(self, request, course_id=None):
        """"
        GET /api/grades/course/<int:pk>/ - Instructor
        Returns a list of grades for a specific course created by the instructor
        """
        course = get_object_or_404(Course, pk=course_id)
        # Check if the instructor is the creator of the course
        if course.created_by != request.user:
            return Response({"detail": "You do not have permission to view these grades."}, status=403)

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
        return Grade.objects.filter(enrollment__user=user)
