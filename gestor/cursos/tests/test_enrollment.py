import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from cursos.models import Enrollment, Course
from .utils import Utils

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def student_user():
    """Create a student user and return username and token"""
    username = "test_student"
    Utils.register_user(username, "student")
    token = Utils.get_token(username)
    return {"username": username, "token": token}

@pytest.fixture
def instructor_user():
    """Create an instructor user and return username and token"""
    username = "test_instructor"
    Utils.register_user(username, "instructor")
    token = Utils.get_token(username)
    return {"username": username, "token": token}

@pytest.fixture
def course(instructor_user):
    """Create a test course and return its ID"""
    response = Utils.create_course("Test Course", "Course description", instructor_user['token'])
    return response.json()

class TestEnrollment:
    def test_create_enrollment_success(self, api_client, student_user, course):
        """Test that a student can successfully enroll in a course"""
        url = reverse('enroll')
        payload = {"course": course['id']}
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_user['token']}")
        response = api_client.post(url, data=payload, format='json')
        
        # Verify response
        assert response.status_code == 201
        assert 'id' in response.json()
        assert response.json()['course'] == course['id']
        
        # Verify database state
        assert Enrollment.objects.filter(
            user__username=student_user['username'],
            course__id=course['id']
        ).exists()
        
    def test_list_enrollments(self, api_client, student_user, course):
        """Test that a student can list their enrollments"""
        # Create enrollment
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_user['token']}")
        api_client.post(reverse('enroll'), data={"course": course['id']}, format='json')
        
        # Get enrollments list
        url = reverse('enrollments-user')
        response = api_client.get(url)
        
        # Verify response
        assert response.status_code == 200
        assert len(response.json()) >= 1
        enrollment = response.json()[0] if isinstance(response.json(), list) else response.json()['results'][0]
        assert enrollment['course'] == course['id']
        
    def test_duplicate_enrollment_fails(self, api_client, student_user, course):
        """Test that enrolling twice in the same course fails"""
        url = reverse('enroll')
        payload = {"course": course['id']}
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_user['token']}")
        
        # First enrollment (success)
        api_client.post(url, data=payload, format='json')
        
        # Second enrollment (should fail)
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 400
        assert 'already enrolled' in str(response.json()).lower()
        
    def test_instructor_cannot_enroll(self, api_client, instructor_user, course):
        """Test that instructors cannot enroll in courses"""
        url = reverse('enroll')
        payload = {"course": course['id']}
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 403
        
    def test_enroll_nonexistent_course_fails(self, api_client, student_user):
        """Test that enrolling in a non-existent course fails"""
        url = reverse('enroll')
        payload = {"course": 99999}  # Non-existent course ID
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_user['token']}")
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 400
