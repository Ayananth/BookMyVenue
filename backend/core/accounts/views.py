from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from accounts.serializers import (
    GoogleLoginSerializer,
    LoginSerializer,
    RegisterSerializer,
    SendSignupOtpSerializer,
    UserSerializer,
    UserUpdateSerializer,
    VerifySignupOtpSerializer,
    build_token_response,
)
from notifications.services.otp_service import (
    OtpMaxAttemptsExceededError,
    OtpNotFoundError,
    OtpResendCooldownError,
)
from notifications.services.redis_client import RedisUnavailableError
from notifications.services.signup_otp_service import SignupOtpService


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


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]
    role = UserRole.USER

    def post(self, request):
        serializer = GoogleLoginSerializer(
            data=request.data,
            context={"role": self.role},
        )
        serializer.is_valid(raise_exception=True)
        return Response(build_token_response(serializer.validated_data["user"]))


class UserGoogleLoginView(GoogleLoginView):
    role = UserRole.USER


class VenueGoogleLoginView(GoogleLoginView):
    role = UserRole.VENUE


class SendSignupOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SendSignupOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = SignupOtpService.send_email_otp(serializer.validated_data["email"])
        except OtpResendCooldownError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except RedisUnavailableError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            {
                "detail": "Verification code sent.",
                **result,
            },
            status=status.HTTP_200_OK,
        )


class VerifySignupOtpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifySignupOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            verified = SignupOtpService.verify_email_otp(email, otp)
        except OtpNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except OtpMaxAttemptsExceededError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except RedisUnavailableError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not verified:
            return Response(
                {"detail": "Invalid verification code."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "verified": True,
                "email": email.strip().lower(),
            },
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)
