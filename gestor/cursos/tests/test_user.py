import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from cursos.models import User

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(api_client):
    payload = {
        "username": "testAdmin", 
        "password": "pass", 
        "role": "admin"
    }
    url = reverse('register')
    response = api_client.post(url, data=payload, format='json')
    user_data = response.json()
    
    # Get token
    token_url = reverse('token_obtain_pair')
    token_response = api_client.post(token_url, data={
        "username": payload["username"],
        "password": payload["password"]
    }, format='json')
    
    return {
        'user': user_data,
        'token': token_response.json()['access'],
        'credentials': payload
    }

class TestUserAuth:
    def test_register_user(self, api_client):
        url = reverse('register')
        payload = {"username": "newUser", "password": "pass", "role": "student"}
        
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 201
        assert response.json()['username'] == payload['username']
        assert response.json()['role'] == payload['role']
        assert 'password' not in response.json()  # Password should not be returned
        
        # Verify user exists in database
        assert User.objects.filter(username=payload['username']).exists()
    
    def test_duplicate_username_fails(self, api_client):
        url = reverse('register')
        payload = {"username": "duplicateUser", "password": "pass", "role": "student"}
        
        # First registration
        api_client.post(url, data=payload, format='json')
        
        # Second registration with same username
        response = api_client.post(url, data=payload, format='json')
        assert response.status_code == 400
        
    def test_invalid_role_fails(self, api_client):
        url = reverse('register')
        payload = {"username": "roleUser", "password": "pass", "role": "invalid_role"}
        
        response = api_client.post(url, data=payload, format='json')
        assert response.status_code == 400

class TestUserAPI:
    def test_list_users_as_admin(self, api_client, admin_user):
        url = reverse('user-list')
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {admin_user['token']}")
        
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert 'results' in response.json()  # Pagination is enabled
        
    def test_list_users_as_student_fails(self, api_client):
        # Register student
        student_payload = {"username": "student1", "password": "pass", "role": "student"}
        api_client.post(reverse('register'), data=student_payload, format='json')
        
        # Get token
        token_response = api_client.post(
            reverse('token_obtain_pair'),
            data={"username": student_payload["username"], "password": student_payload["password"]},
            format='json'
        )
        token = token_response.json()['access']
        
        # Try to access user list
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = api_client.get(reverse('user-list'))
        
        assert response.status_code == 403  # Forbidden
