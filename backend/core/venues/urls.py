from django.urls import path

from venues.views import (
    ImageUploadView,
    VenueCategoryListView,
    VenueCreateView,
    VenueDetailView,
    VenueListCreateView,
    VenueLocationListView,
)

urlpatterns = [
    path("categories", VenueCategoryListView.as_view(), name="venue-categories"),
    path("locations", VenueLocationListView.as_view(), name="venue-locations"),
    path("", VenueListCreateView.as_view(), name="venue-list-create"),
    path("add", VenueCreateView.as_view(), name="venue-add"),
    path("<slug:slug>/", VenueDetailView.as_view(), name="venue-detail"),
]
