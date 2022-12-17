from django.contrib.auth import login
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response

from core.models import User
from core.serializers import CreateUserSerializer, LoginUserSerializer, UserSerializer


class SignupView(CreateAPIView):
    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = CreateUserSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        login(self.request, user=serializer.user)


class LoginView(GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user=user)
        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)



