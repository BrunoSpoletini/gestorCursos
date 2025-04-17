from rest_framework.test import APIClient
from django.urls import reverse
import pytest
from .utils import Utils

pytestmark = pytest.mark.django_db
client = APIClient()


class TestEnrollment():

    def test_create_enrollment(self):
        Utils.register_user("testUserStudent", "student")
        Utils.register_user("testUserInstructor", "instructor")
        instructor_token = Utils.get_token("testUserInstructor")
        create_course_response = Utils.create_course("Mecanografia", "loreipsum", instructor_token)
        course_id = create_course_response.json().get('id')
        student_token = Utils.get_token("testUserStudent")
        enroll_student_response = Utils.enroll_student(course_id, student_token)
        print(f"Student enrollment response:\n{enroll_student_response.json()}")
        assert enroll_student_response.status_code == 201

    
    def test_list_enrollments_user(self):
        Utils.register_user("testUserStudent", "student")
        Utils.register_user("testUserInstructor", "instructor")
        instructor_token = Utils.get_token("testUserInstructor")
        create_course_response = Utils.create_course("Mecanografia", "loreipsum", instructor_token)
        course_id = create_course_response.json().get('id')
        student_token = Utils.get_token("testUserStudent")
        Utils.enroll_student(course_id, student_token)
        url = reverse('enrollments-user')
        enroll_list_response = client.get(url, HTTP_AUTHORIZATION=f"Bearer {student_token}")
        print(f"Enrollment list response:\n{enroll_list_response.json()}")
        assert enroll_list_response.status_code == 200
