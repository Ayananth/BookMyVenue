from django.urls import path

from venues.views import VenueCreateView, VenueDetailView, VenueListCreateView

urlpatterns = [
    path("", VenueListCreateView.as_view(), name="venue-list-create"),
    path("add", VenueCreateView.as_view(), name="venue-add"),
    path("<slug:slug>/", VenueDetailView.as_view(), name="venue-detail"),
]
