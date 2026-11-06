from rest_framework import serializers
from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer,
)
from django.contrib.auth.password_validation import validate_password as django_validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
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
            "is_active",
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
        request = self.context.get("request")
        password = attrs.get("password")

        # Password is required when creating a user
        if self.instance is None and not password:
            raise serializers.ValidationError({
                "password": "This field is required."
            })

        # Validate password strength on create and password update
        if password:
            if self.instance:
                user = self.instance
            else:
                user = User(**{
                    key: value
                    for key, value in attrs.items()
                    if key != "password"
                })

            try:
                django_validate_password(password, user=user)
            except DjangoValidationError as error:
                raise serializers.ValidationError({
                    "password": list(error.messages)
                })

        # Prevent users from changing their own role or deactivating themselves
        if self.instance and request:
            if self.instance.pk == request.user.pk:
                if "role" in attrs:
                    raise serializers.ValidationError({
                        "role": "You cannot change your own role."
                    })

                if attrs.get("is_active") is False:
                    raise serializers.ValidationError({
                        "is_active": "You cannot deactivate your own account."
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
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "address",
            "phone_number",
            "profile_image",
            "date_of_birth",
            "gender",
            "role",
            "is_staff",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
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

