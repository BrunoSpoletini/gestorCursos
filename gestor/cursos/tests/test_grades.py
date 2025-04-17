from rest_framework.test import APIClient
from django.urls import reverse
import pytest
from .utils import Utils

pytestmark = pytest.mark.django_db
client = APIClient()


class TestGrades():

    def test_grade_student(self):
        Utils.register_user("testUserStudent", "student")
        Utils.register_user("testUserInstructor", "instructor")
        instructor_token = Utils.get_token("testUserInstructor")
        create_course_response = Utils.create_course("Mecanografia", "loreipsum", instructor_token)
        course_id = create_course_response.json().get('id')
        student_token = Utils.get_token("testUserStudent")
        enroll_student_response = Utils.enroll_student(course_id, student_token)
        enrollment_id = enroll_student_response.json().get('id')
        grade_student_response = Utils.grade_student(enrollment_id, 10, "Good job :)", instructor_token)
        print(f"Grade student response:\n{enroll_student_response.json()}")
        assert grade_student_response.status_code == 201

    def test_list_grades_student(self):
        Utils.register_user("testUserStudent", "student")
        Utils.register_user("testUserInstructor", "instructor")
        instructor_token = Utils.get_token("testUserInstructor")
        create_course_response = Utils.create_course("Mecanografia", "loreipsum", instructor_token)
        course_id = create_course_response.json().get('id')
        student_token = Utils.get_token("testUserStudent")
        enroll_student_response = Utils.enroll_student(course_id, student_token)
        enrollment_id = enroll_student_response.json().get('id')
        Utils.grade_student(enrollment_id, 10, "Good job :)", instructor_token)
        url = reverse('grades-student')
        get_grades_response = client.get(url, HTTP_AUTHORIZATION=f"Bearer {student_token}")
        print(f"Grades list for student response:\n{get_grades_response.json()}")
        assert get_grades_response.status_code == 200

    def test_list_grades_instructor_course(self):
        Utils.register_user("testUserStudent", "student")
        Utils.register_user("testUserInstructor", "instructor")
        instructor_token = Utils.get_token("testUserInstructor")
        create_course_response = Utils.create_course("Mecanografia", "loreipsum", instructor_token)
        course_id = create_course_response.json().get('id')
        student_token = Utils.get_token("testUserStudent")
        enroll_student_response = Utils.enroll_student(course_id, student_token)
        enrollment_id = enroll_student_response.json().get('id')
        Utils.grade_student(enrollment_id, 10, "Good job :)", instructor_token)
        url = reverse('grades-instructor-grades-by-course', args=[course_id])
        get_grades_response = client.get(url, HTTP_AUTHORIZATION=f"Bearer {instructor_token}")
        print(f"Grades list for instructor response:\n{get_grades_response.json()}")
        assert get_grades_response.status_code == 200
