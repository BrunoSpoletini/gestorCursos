import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.conf import settings
from cursos.models import Course
from .utils import Utils

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def instructor_user(api_client):
    """Create an instructor and return their credentials and token"""
    username = "test_instructor"
    Utils.register_user(username, "instructor")
    token = Utils.get_token(username)
    return {"username": username, "token": token}

class TestCourse:
    def test_create_course_success(self, api_client, instructor_user):
        """Test successful course creation by an instructor"""
        url = reverse('courses-list')
        payload = {"name": "Test Course", "description": "Course description"}
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 201
        assert response.json()['name'] == payload['name']
        assert response.json()['description'] == payload['description']
        assert response.json()['created_by'] == instructor_user['username']
        # Verify database state
        assert Course.objects.filter(name=payload['name']).exists()
    
    def test_create_duplicate_course_fails(self, api_client, instructor_user):
        """Test that creating a course with a duplicate name fails"""
        url = reverse('courses-list')
        payload = {"name": "Duplicate Course", "description": "Course description"}
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        # First creation should succeed
        api_client.post(url, data=payload, format='json')
        
        # Second creation should fail
        response = api_client.post(url, data=payload, format='json')
        assert response.status_code == 400
        assert 'name' in response.json()
    
    def test_student_cannot_create_course(self, api_client):
        """Test that students cannot create courses"""
        Utils.register_user("test_student", "student")
        student_token = Utils.get_token("test_student")
        
        url = reverse('courses-list')
        payload = {"name": "Student Course", "description": "Course description"}
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_token}")
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 403
        
    def test_course_listing_pagination(self, api_client, instructor_user):
        """Test course listing with pagination"""
        # Create multiple courses
        url = reverse('courses-list')
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        pagination_size = getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE')

        # Create more courses than the pagination size
        for i in range(pagination_size + 2):
            api_client.post(
                url, 
                data={"name": f"Course {i}", "description": "Test description"},
                format='json'
            )
        
        # Test first page
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.json()['count'] >= (pagination_size + 2)
        assert 'next' in response.json()
        assert len(response.json()['results']) == pagination_size
        
        # Test second page
        response = api_client.get(response.json()['next'])
        assert response.status_code == 200
        assert len(response.json()['results']) > 0