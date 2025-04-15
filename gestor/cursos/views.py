from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, generics
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




# # POST /api/grades/
# class GradeStudentView(generics.CreateAPIView):
#     queryset = Grade.objects.all()
#     serializer_class = GradesSerializer
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAdmin | IsInstructor]


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
        return Grade.objects.filter(enrollment__user=user)