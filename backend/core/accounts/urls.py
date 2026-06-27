from django.urls import path

from accounts.views import (
    MeView,
    UserLoginView,
    UserRegisterView,
    VenueLoginView,
    VenueRegisterView,
)

urlpatterns = [
    path("register", UserRegisterView.as_view(), name="user-register"),
    path("login", UserLoginView.as_view(), name="user-login"),
    path("me", MeView.as_view(), name="user-me"),
    path("venue/register", VenueRegisterView.as_view(), name="venue-register"),
    path("venue/login", VenueLoginView.as_view(), name="venue-login"),
]
