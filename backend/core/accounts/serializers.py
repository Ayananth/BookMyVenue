from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.google_auth import login_or_register_with_google, verify_google_id_token
from accounts.models import User, UserRole
from accounts.security import create_access_token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "phone",
            "avatar_url",
            "role",
            "is_active",
            "is_blocked",
            "is_email_verified",
            "is_phone_verified",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    full_name = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
    )

    def validate_email(self, value):
        email = User.objects.normalize_email(value)
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Email already registered.")
        return email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        role = self.context["role"]
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data.get("full_name") or None,
            role=role,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = User.objects.normalize_email(attrs["email"])
        expected_role = self.context["role"]

        user = User.objects.filter(email__iexact=email).first()
        if user and user.role != expected_role:
            raise serializers.ValidationError(
                {
                    "email": (
                        f"This email is associated with a {user.role} account."
                    ),
                },
            )

        authenticated_user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=attrs["password"],
        )
        if authenticated_user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."},
            )

        if not authenticated_user.is_active or authenticated_user.is_blocked:
            raise serializers.ValidationError(
                {"detail": "Account is disabled."},
            )

        attrs["user"] = authenticated_user
        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        info = verify_google_id_token(attrs["token"])
        role = self.context["role"]
        attrs["user"] = login_or_register_with_google(info, role)
        return attrs


def build_token_response(user: User) -> dict:
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": UserSerializer(user).data,
    }
