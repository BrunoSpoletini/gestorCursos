from django.contrib.auth.models import Group
from rest_framework import mixins, permissions, viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from . permissions import IsInstructor, IsStudent, IsAdmin
from django.contrib.auth import get_user_model
from . serializers import UserSerializer, CourseSerializer, GradesSerializer, EnrollmentSerializer
from . models import Course, Grade, Enrollment

User = get_user_model()

# GET /api/users/
# Returns a list of all users
class UserView(generics.ListAPIView):  
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

# POST /api/register/
# Allows users to register with a username, password and role
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# GET /api/courses/
# Returns a list of all courses
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

# GET /api/courses/<int:pk>/
# Returns details of a specific course
class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.AllowAny]

# POST /api/courses/create/
# Allows instructors to create a new course
class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsInstructor]

# POST /api/grades/
# GET /api/grades/course/<int:pk>/
class GradeInstructorView(  mixins.CreateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsInstructor]

    @action(detail=False, methods=['get'], url_path='course/(?P<course_id>[^/.]+)')
    def grades_by_course(self, request, course_id=None):
        
        try:
            # Attempt to retrieve the course
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            # Return a 404 response if the course does not exist
            return Response({"detail": "Course not found."}, status=404)

        # Check if the instructor is the creator of the course
        if course.created_by != request.user:
            return Response({"detail": "You do not have permission to view these grades."}, status=403)

        # Retrieve grades for 
        grades = Grade.objects.filter(enrollment__course=course)
        serializer = self.get_serializer(grades, many=True)
        return Response(serializer.data)

# GET /api/my-grades/
class GradeStudentView(generics.ListAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradesSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]
    def get_queryset(self):
        user = self.request.user
        return Grade.objects.filter(enrollment__user=user)

# POST /api/enroll/
class EnrollmentView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# GET /api/my-enrollments/
class EnrollmentsUserView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin | IsStudent]

    def get_queryset(self):
        user = self.request.user
        return Enrollment.objects.filter(user=user)