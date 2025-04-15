from rest_framework import routers
from .views import UserView, UserRegisterView, CourseListView, CourseDetailView, CourseCreateView, EnrollmentView, EnrollmentsUserView
from django.urls import path

urlpatterns = [
    # Users API
    path('users/', UserView.as_view(), name='user-list'),
    path('register/', UserRegisterView.as_view(), name='register'),
    
    # Courses API
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),

    # # Grades API - TO DO
    # path('grades/', CourseListView.as_view(), name='grade-create'),
    # path('grades/course/<int:pk>/', CourseCreateView.as_view(), name='grades-course'),
    # path('my-grades/', CourseDetailView.as_view(), name='grades-student'),

    # Enrollments API
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-enrollments/', EnrollmentsUserView.as_view(), name='enrollments-user'),


]