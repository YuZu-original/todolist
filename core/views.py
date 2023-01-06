from django.contrib.auth import login
from django.contrib.auth import logout
from rest_framework import permissions
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response

from core.models import User
from core.serializers import CreateUserSerializer
from core.serializers import LoginUserSerializer
from core.serializers import UpdatePasswordSerializer
from core.serializers import UserSerializer


class SignupView(CreateAPIView):
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        login(
            self.request,
            user=serializer.user,
            backend="django.contrib.auth.backends.ModelBackend",
        )


class LoginView(GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user=user)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)


class ProfileView(RetrieveUpdateDestroyAPIView):
    model = User
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        logout(request)
        return Response({})


class UpdatePasswordView(UpdateAPIView):
    model = User
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def get_object(self):
        return self.request.user
