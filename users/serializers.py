
from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer,
)

from users.models import User


class UserCRUDSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "address",
            "phone_number",
            "profile_image",
            "date_of_birth",
            "gender",
            "role",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "date_joined",
            "last_login",
        ]
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({
                "password": "This field is required."
            })

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(
            password=password,
            **validated_data,
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])

        return instance


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "address",
            "phone_number",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }


class UserViewSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "address",
            "phone_number",
            "is_staff",
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "address",
            "phone_number",
            "profile_image",
            "date_of_birth",
            "gender",
        ]