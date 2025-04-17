from rest_framework.test import APIClient
from django.urls import reverse
import pytest

pytestmark = pytest.mark.django_db
client = APIClient()

class Utils():
    @staticmethod
    def register_user(username, role):
        payload = {
            "username": username,
            "password": "pass",
            "role": role
        }
        url = reverse('register')
        response = client.post(url, data=payload, format='json')
        if response.status_code == 201:
            return response
        else:
            raise Exception(f"Error registering user: {response.json()}")
    
    @staticmethod
    def get_token(username):
        url = reverse('token_obtain_pair')
        response = client.post(url, data={
            "username": username,
            "password": "pass"
        }, format='json')
        if response.status_code != 200:
            raise Exception(f"Error obtaining token: {response.json()}")
        # Check if the response contains the access token
        if "access" not in response.json():
            raise Exception("Access token not found in the response")
        # Return the access token
        return response.json().get("access")
    
    @staticmethod
    def create_course(name, description, token):
        payload = {
            "name": name,
            "description": description,
        }
        url = reverse('courses-list')
        response = client.post(url, data=payload, format='json', HTTP_AUTHORIZATION=f"Bearer {token}")
        if response.status_code == 201:
            return response
        else:
            raise Exception(f"Error creating course: {response.json()}")
    
    @staticmethod
    def enroll_student(course_id, token):
        payload = {
            "course": course_id
        }
        url = reverse('enroll')
        response = client.post(url, data=payload, format='json', HTTP_AUTHORIZATION=f"Bearer {token}")
        if response.status_code == 201:
            return response
        else:
            raise Exception(f"Error enrolling student: {response.json()}")

    @staticmethod
    def grade_student(enrollment, score, comment, token):
        payload = {
            "enrollment": enrollment,
            "score": score,
            "comment": comment
        }
        url = reverse('grades-instructor-list')
        response = client.post(url, data=payload, format='json', HTTP_AUTHORIZATION=f"Bearer {token}")
        if response.status_code == 201:
            return response
        else:
            raise Exception(f"Error grading student: {response.json()}")