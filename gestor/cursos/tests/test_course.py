from rest_framework.test import APIClient
from django.urls import reverse
import pytest
from .utils import Utils

pytestmark = pytest.mark.django_db
client = APIClient()


class TestCourse():

    def test_create_course(self):
        Utils.register_user("testUserInstructor", "instructor")
        token = Utils.get_token("testUserInstructor")
        response = Utils.create_course("Mecanografia", "loreipsum", token)
        print(f"Course creation response:\n{response.json()}")
        assert response.status_code == 201
    
    def test_list_course(self):

        Utils.register_user("testUserInstructor", "instructor")
        token = Utils.get_token("testUserInstructor")
        Utils.create_course("Mecanografia", "loreipsum", token)
        Utils.create_course("Computacion", "loreipsum", token)
        url = reverse('courses-list')
        get_response = client.get(url)
        course_list = get_response.json().get('results')
        print(f"Course list response:\n{course_list}")
        assert get_response.status_code == 200
        assert len(course_list) == 2

    def test_get_course(self):
        Utils.register_user("testUserInstructor", "instructor")
        token = Utils.get_token("testUserInstructor")
        response = Utils.create_course("Mecanografia", "loreipsum", token)
        course_id = response.json().get('id')
        url = reverse('courses-detail', args=[course_id])
        get_response = client.get(url)
        print(f"Get course response:\n{get_response.json()}")
        assert get_response.status_code == 200
        assert get_response.json().get('name') == "Mecanografia"