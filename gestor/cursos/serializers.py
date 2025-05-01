from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Course, Enrollment, Grade

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "password", "role"]

    def create(self, data):
        return User.objects.create_user(**data)


class CourseSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    name = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=Course.objects.all(),
                message="Course with this name already exists.",
            )
        ]
    )

    class Meta:
        model = Course
        fields = ["id", "name", "description", "created_by"]

    def create(self, data):
        user = self.context["request"].user
        data["created_by"] = user
        return Course.objects.create(**data)


class EnrollmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        error_messages={
            "does_not_exist": "Course does not exist.",
            "invalid": "Invalid course.",
        },
    )

    class Meta:
        model = Enrollment
        fields = ["id", "user", "course", "created_at"]

    def validate(self, data):
        user = self.context["request"].user
        course = data.get("course")

        # Check if the user is already enrolled
        if Enrollment.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError(
                "User is already enrolled in this course."
            )
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        return Enrollment.objects.create(user=user, **validated_data)


class GradesSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    enrollment = serializers.PrimaryKeyRelatedField(
        queryset=Enrollment.objects.all(),
        validators=[
            UniqueValidator(
                queryset=Grade.objects.all(),
                message="Grade for this enrollment already exists.",
            )
        ],
        error_messages={
            "does_not_exist": "Enrollment does not exist.",
            "invalid": "Invalid enrollment.",
        },
    )

    def validate_enrollment(self, enrollment):
        user = self.context["request"].user

        # Check if the user is the instructor of the course
        course = enrollment.course
        if course.created_by != user:
            raise serializers.ValidationError(
                "You do not have permission to grade this enrollment."
            )
        return enrollment

    def validate_score(self, value):
        if not (0 <= value <= 10):
            raise serializers.ValidationError("Score must be between 0 and 10.")
        return value

    class Meta:
        model = Grade
        fields = ["id", "enrollment", "created_at", "score", "comment"]
        validators = [
            UniqueTogetherValidator(
                queryset=Grade.objects.all(),
                fields=["enrollment"],
                message="Grade for this enrollment already exists.",
            )
        ]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data