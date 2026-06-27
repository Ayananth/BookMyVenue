from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from accounts.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    build_token_response,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    role = UserRole.USER

    def post(self, request):
        serializer = RegisterSerializer(
            data=request.data,
            context={"role": self.role},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            build_token_response(user),
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]
    role = UserRole.USER

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"role": self.role, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        return Response(build_token_response(serializer.validated_data["user"]))


class UserRegisterView(RegisterView):
    role = UserRole.USER


class UserLoginView(LoginView):
    role = UserRole.USER


class VenueRegisterView(RegisterView):
    role = UserRole.VENUE


class VenueLoginView(LoginView):
    role = UserRole.VENUE


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
