from rest_framework import serializers
from django.contrib.auth import get_user_model
from . models import Course, Enrollment, Grade

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role']
    
    def create(self, data):
        return User.objects.create_user(**data)

class CourseSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'created_by']

    def create(self, data):
        user = self.context['request'].user
        data['created_by'] = user
        return Course.objects.create(**data)


class GradesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    enrollment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'created_at', 'id_course', 'score', 'comment']
# TO-DO
    # def create(self, data):
    #     request = self.context['request']
    #     course = Course.objects.get(id=data['id_course'])
    #     enrollment = Enrollment.objects.get(user=request.user, course=course)

    #     data['enrollment'] = enrollment
    #     return Grade.objects.create(**data)
    
class EnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'created_at']

    def create(self, data):
        enrollment = Enrollment(**data)
        if enrollment.validate_enrollment():
            enrollment.save()
        else:
            raise serializers.ValidationError("User is already enrolled in this course.")
        return enrollment
