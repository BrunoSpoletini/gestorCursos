from rest_framework import routers
from .views import UserView, UserRegisterView
from django.urls import path

urlpatterns = [
    path('users/', UserView.as_view(), name='user-list'),
    path('register/', UserRegisterView.as_view(), name='register'),
]