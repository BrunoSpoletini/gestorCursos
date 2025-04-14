from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsInstructor, IsStudent, IsAdmin
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

# GET /users/
# Returns a list of all users
class UserView(generics.ListAPIView):  
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdmin]

# POST /register/
# Allows users to register with a username, password and role
class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]