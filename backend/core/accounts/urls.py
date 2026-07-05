from django.urls import path

from accounts.views import (
    MeView,
    SendSignupOtpView,
    UserGoogleLoginView,
    UserLoginView,
    UserRegisterView,
    VenueGoogleLoginView,
    VenueLoginView,
    VenueRegisterView,
    VerifySignupOtpView,
)

urlpatterns = [
    path("register", UserRegisterView.as_view(), name="user-register"),
    path("register/send-otp", SendSignupOtpView.as_view(), name="user-send-signup-otp"),
    path("register/verify-otp", VerifySignupOtpView.as_view(), name="user-verify-signup-otp"),
    path("login", UserLoginView.as_view(), name="user-login"),
    path("google", UserGoogleLoginView.as_view(), name="user-google-login"),
    path("me", MeView.as_view(), name="user-me"),
    path("venue/register", VenueRegisterView.as_view(), name="venue-register"),
    path("venue/register/send-otp", SendSignupOtpView.as_view(), name="venue-send-signup-otp"),
    path("venue/register/verify-otp", VerifySignupOtpView.as_view(), name="venue-verify-signup-otp"),
    path("venue/login", VenueLoginView.as_view(), name="venue-login"),
    path("venue/google", VenueGoogleLoginView.as_view(), name="venue-google-login"),
]
