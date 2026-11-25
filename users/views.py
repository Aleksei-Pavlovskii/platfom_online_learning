from rest_framework import generics
from rest_framework.permissions import AllowAny

from lms.serializers import UserSerializer
from .serializers import UserRegisterSerializer

class UserRegisterAPIView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserDestroyAPIView(generics.DestroyAPIView):
    serializer_class = UserSerializer