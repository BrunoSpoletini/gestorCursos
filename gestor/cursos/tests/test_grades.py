import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.conf import settings
from cursos.models import Grade
from .utils import Utils

pytestmark = pytest.mark.django_db

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def student_user():
    """Create a student and return username and token"""
    username = "test_student_grades"
    Utils.register_user(username, "student")
    token = Utils.get_token(username)
    return {"username": username, "token": token}

@pytest.fixture
def instructor_user():
    """Create an instructor and return username and token"""
    username = "test_instructor_grades"
    Utils.register_user(username, "instructor")
    token = Utils.get_token(username)
    return {"username": username, "token": token}

@pytest.fixture
def course(instructor_user):
    """Create a test course and return its data"""
    response = Utils.create_course("Test Course Grading", "Course description", instructor_user['token'])
    return response.json()

@pytest.fixture
def enrollment(course, student_user):
    """Create a student enrollment and return its data"""
    response = Utils.enroll_student(course['id'], student_user['token'])
    return response.json()

@pytest.fixture
def grade(enrollment, instructor_user):
    """Create a grade and return its data"""
    response = Utils.grade_student(enrollment['id'], 8.5, "Good work", instructor_user['token'])
    return response.json()

class TestGrades:
    def test_grade_student_success(self, api_client, enrollment, instructor_user):
        """Test that an instructor can successfully grade a student"""
        url = reverse('grades-instructor-list')
        payload = {
            "enrollment": enrollment['id'],
            "score": 9.5,
            "comment": "Great performance"
        }
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        response = api_client.post(url, data=payload, format='json')
        
        # Verify response
        assert response.status_code == 201
        assert response.json()['score'] == '9.5'
        assert response.json()['comment'] == "Great performance"
        
        # Verify database state
        assert Grade.objects.filter(enrollment=enrollment['id']).exists()

    def test_grade_student_unauthorized_course(self, api_client, enrollment):
        """Test that an instructor cannot grade students in courses they don't own"""
        # Create another instructor
        Utils.register_user("other_instructor", "instructor")
        other_token = Utils.get_token("other_instructor")
        
        url = reverse('grades-instructor-list')
        payload = {
            "enrollment": enrollment['id'],
            "score": 9.5,
            "comment": "Nice work"
        }
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {other_token}")
        response = api_client.post(url, data=payload, format='json')
        
        # Should be forbidden or validation error
        assert response.status_code in (400, 403)
        
    def test_invalid_grade_value(self, api_client, enrollment, instructor_user):
        """Test that invalid grade values are rejected"""
        url = reverse('grades-instructor-list')
        payload = {
            "enrollment": enrollment['id'],
            "score": 11,  # Invalid score > 10
            "comment": "Invalid score"
        }
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        response = api_client.post(url, data=payload, format='json')
        
        assert response.status_code == 400
        assert 'score' in response.json()

    def test_list_grades_student(self, api_client, grade, student_user):
        """Test that a student can view their own grades"""
        url = reverse('grades-student')
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {student_user['token']}")
        response = api_client.get(url)
        
        assert response.status_code == 200
        grades = response.json()
        
        # Check if this is a paginated response
        if isinstance(grades, dict) and 'results' in grades:
            grades = grades['results']
            
        assert len(grades) >= 1
        assert str(grade['id']) in [str(g['id']) for g in grades]
        
    def test_list_grades_instructor_course(self, api_client, grade, course, instructor_user):
        """Test that an instructor can view grades for their courses"""
        url = reverse('grades-instructor-grades-by-course', args=[course['id']])
        
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {instructor_user['token']}")
        response = api_client.get(url)
        
        assert response.status_code == 200
        grades = response.json()
        
        # Check if this is a paginated response
        if isinstance(grades, dict) and 'results' in grades:
            grades = grades['results']
            
        assert len(grades) >= 1
        assert str(grade['id']) in [str(g['id']) for g in grades]
