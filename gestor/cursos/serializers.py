from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

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
    name = serializers.CharField(validators=[UniqueValidator(queryset=Course.objects.all())]) 

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'created_by']

    def create(self, data):
        user = self.context['request'].user
        data['created_by'] = user
        return Course.objects.create(**data)
    
class EnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        course = data.get('course')

        # Check if the user is already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError("User is already enrolled in this course.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        return Enrollment.objects.create(user=user, **validated_data)

class GradesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)

    def validate_enrollment(self, enrollment):
        user = self.context['request'].user

        # Check if the user is the instructor of the course
        course = enrollment.course
        if (course.created_by != user):
            raise serializers.ValidationError("You do not have permission to grade this enrollment.")
        return enrollment

    def validate_score(self, value):
        if not (0 <= value <= 10):
            raise serializers.ValidationError("Score must be between 0 and 10.")
        return value

    class Meta:
        model = Grade
        fields = ['id', 'enrollment', 'created_at', 'score', 'comment']
        validators = [
            UniqueTogetherValidator(
                queryset=Grade.objects.all(),
                fields=['enrollment'],
                message="Grade for this enrollment already exists."
            )
        ]