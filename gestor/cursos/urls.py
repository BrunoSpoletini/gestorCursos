from django.urls import include, path
from rest_framework import routers

from .views import (
    CourseViewSet,
    EnrollmentsUserView,
    EnrollmentView,
    GradeView,
    GradeInstructorView,
    GradeStudentView,
    UserRegisterView,
    UserView,
)

router = routers.DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
    # Users Endpoints
    path("users/", UserView.as_view(), name="user-list"),
    path("register/", UserRegisterView.as_view(), name="register"),
    # Grades Endpoints
    path("grades/", GradeView.as_view(), name="instructor-grade"),
    path("grades/course/<int:course_id>/", GradeInstructorView.as_view(), name="grades-instructor-detail"),
    path("my-grades/", GradeStudentView.as_view(), name="grades-student"),
    # Enrollments Endpoints
    path("enroll/", EnrollmentView.as_view(), name="enroll"),
    path("my-enrollments/", EnrollmentsUserView.as_view(), name="enrollments-user"),
    path("", include(router.urls)),
]
