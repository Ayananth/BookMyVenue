from django.urls import path

from accounts.views import (
    MeView,
    UserGoogleLoginView,
    UserLoginView,
    UserRegisterView,
    VenueGoogleLoginView,
    VenueLoginView,
    VenueRegisterView,
)

urlpatterns = [
    path("register", UserRegisterView.as_view(), name="user-register"),
    path("login", UserLoginView.as_view(), name="user-login"),
    path("google", UserGoogleLoginView.as_view(), name="user-google-login"),
    path("me", MeView.as_view(), name="user-me"),
    path("venue/register", VenueRegisterView.as_view(), name="venue-register"),
    path("venue/login", VenueLoginView.as_view(), name="venue-login"),
    path("venue/google", VenueGoogleLoginView.as_view(), name="venue-google-login"),
]
