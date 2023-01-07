from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import User


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )
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
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_repeat",
        )


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs: dict):
        username = attrs.get("username")
        password = attrs.get("password")
        print(attrs)
        user = authenticate(username=username, password=password)
        print(user)
        if user is None:
            raise ValidationError("username or password is incorrect")
        print(user.username, user.password)
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        read_only_fields = ("id",)
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        )


class UpdatePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password]
    )

    def validate(self, attrs):
        old_password = attrs.get("old_password")
        user = self.instance

        if not user.check_password(old_password):
            raise ValidationError({"old_password": "field is incorrect"})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save(update_fields=["password"])
        return instance

    class Meta:
        model = User
        read_only_fields = ("id",)
        fields = ("old_password", "new_password")
