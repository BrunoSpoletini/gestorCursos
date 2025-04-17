import requests
from rest_framework.test import APIClient
from django.urls import reverse
import pytest
from .utils import Utils

pytestmark = pytest.mark.django_db
client = APIClient()


class TestUser():

    def test_register_user(self):
        response = Utils.register_user("testUser", "admin")
        print(f"User registration response:\n{response.json()}")
        assert response.status_code == 201
    
    def test_login_user(self):
        Utils.register_user("testUser", "admin")
        url = reverse('token_obtain_pair')
        response = client.post(url, data={
            "username": "testUser",
            "password": "pass"
        }, format='json')
        print(f"Login response:\n{response.json()}")
        assert response.status_code == 200

    def test_list_user(self):
        Utils.register_user("testUserAdmin", "admin")
        Utils.register_user("testUserStudent", "student")
        Utils.register_user("testUserInstructor", "instructor")
        token = Utils.get_token("testUserAdmin")
        url = reverse('user-list')
        response = client.get(url, HTTP_AUTHORIZATION=f"Bearer {token}")
        print(f"User list response:\n{response.json()}")
        assert response.status_code == 200
