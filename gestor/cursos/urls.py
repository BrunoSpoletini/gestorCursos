from rest_framework import routers
from .views import UserView, UserRegisterView, CourseListView, CourseDetailView, CourseCreateView, EnrollmentView, EnrollmentsUserView, GradeInstructorView, GradeStudentView
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'grades', GradeInstructorView, basename='grades-instructor')

urlpatterns = [
    # Users Endpoints
    path('users/', UserView.as_view(), name='user-list'),
    path('register/', UserRegisterView.as_view(), name='register'),
    
    # Courses Endpoints
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),

    # # Grades Endpoints
    path('', include(router.urls)),
    # # path('grades/', GradeInstructorView.as_view(), name='grade-create'),
    #path('grades/course/<int:pk>/', GradeInstructorView.as_view(), name='grades-course'),
    path('my-grades/', GradeStudentView.as_view(), name='grades-student'),

    # Enrollments Endpoints
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-enrollments/', EnrollmentsUserView.as_view(), name='enrollments-user'),


]