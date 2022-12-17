from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_repeat = serializers.CharField(write_only=True)

    def validate(self, attrs: dict):
        password = attrs.get("password")
        password_repeat = attrs.pop("password_repeat", None)

        if password != password_repeat:
            raise ValidationError("password is not equal to password_repeat")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        self.user = user
        return user

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "password", "password_repeat",)


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict):
        username = attrs.get("username")
        password = attrs.get("password")
        user = authenticate(username=username, password=password)

        if not user:
            raise ValidationError("username or password is incorrect")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ("id",)
        fields = ("id", "username", "first_name", "last_name", "email",)
