from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import UserRole
from accounts.serializers import (
    GoogleLoginSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResendSignupOtpSerializer,
    UserSerializer,
    UserUpdateSerializer,
    VerifySignupOtpSerializer,
    build_token_response,
)
from accounts.services.signup_session_service import (
    SignupMaxAttemptsExceededError,
    SignupResendCooldownError,
    SignupRoleMismatchError,
    SignupSessionError,
    SignupSessionNotFoundError,
    SignupSessionService,
)
from notifications.services.redis_client import RedisUnavailableError


class RegisterView(APIView):
    permission_classes = [AllowAny]
    role = UserRole.USER

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = SignupSessionService.start_signup(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                full_name=serializer.validated_data.get("full_name"),
                role=self.role,
            )
        except SignupResendCooldownError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except RedisUnavailableError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            {
                "detail": "Verification code sent. Complete signup with the OTP.",
                **result,
            },
            status=status.HTTP_200_OK,
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


class ResendSignupOtpView(APIView):
    permission_classes = [AllowAny]
    role = UserRole.USER

    def post(self, request):
        serializer = ResendSignupOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = SignupSessionService.resend_otp(
                email=serializer.validated_data["email"],
                role=self.role,
            )
        except SignupSessionNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SignupRoleMismatchError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SignupResendCooldownError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except RedisUnavailableError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            {
                "detail": "Verification code resent.",
                **result,
            },
            status=status.HTTP_200_OK,
        )


class VerifySignupOtpView(APIView):
    permission_classes = [AllowAny]
    role = UserRole.USER

    def post(self, request):
        serializer = VerifySignupOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = SignupSessionService.verify_and_create_user(
                email=email,
                otp=otp,
                role=self.role,
            )
        except SignupSessionNotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SignupRoleMismatchError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except SignupMaxAttemptsExceededError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        except SignupSessionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except RedisUnavailableError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            build_token_response(user),
            status=status.HTTP_201_CREATED,
        )


class UserResendSignupOtpView(ResendSignupOtpView):
    role = UserRole.USER


class VenueResendSignupOtpView(ResendSignupOtpView):
    role = UserRole.VENUE


class UserVerifySignupOtpView(VerifySignupOtpView):
    role = UserRole.USER


class VenueVerifySignupOtpView(VerifySignupOtpView):
    role = UserRole.VENUE


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
