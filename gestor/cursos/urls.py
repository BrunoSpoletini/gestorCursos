from rest_framework import routers
from .views import UserView, UserRegisterView, CourseViewSet, EnrollmentView, EnrollmentsUserView, GradeInstructorViewSet, GradeStudentView
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'grades', GradeInstructorViewSet, basename='grades-instructor')
router.register(r'courses', CourseViewSet, basename='courses')

urlpatterns = [
    # Users Endpoints
    path('users/', UserView.as_view(), name='user-list'),
    path('register/', UserRegisterView.as_view(), name='register'),
    
    # # Grades Endpoints
    path('my-grades/', GradeStudentView.as_view(), name='grades-student'),

    # Enrollments Endpoints
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-enrollments/', EnrollmentsUserView.as_view(), name='enrollments-user'),
    
    path('', include(router.urls)),


]