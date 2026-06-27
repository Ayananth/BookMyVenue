from django.urls import path

from venues.views import (
    ImageUploadView,
    VenueCategoryListView,
    VenueCreateView,
    VenueDetailView,
    VenueListCreateView,
    VenueLocationListView,
    VenueScheduleGroupDetailView,
    VenueScheduleGroupListCreateView,
    VenueScheduleOverrideDetailView,
    VenueScheduleOverrideListCreateView,
)

urlpatterns = [
    path("categories", VenueCategoryListView.as_view(), name="venue-categories"),
    path("locations", VenueLocationListView.as_view(), name="venue-locations"),
    path("", VenueListCreateView.as_view(), name="venue-list-create"),
    path("add", VenueCreateView.as_view(), name="venue-add"),
    path(
        "<slug:slug>/schedule-groups/",
        VenueScheduleGroupListCreateView.as_view(),
        name="venue-schedule-group-list-create",
    ),
    path(
        "<slug:slug>/schedule-groups/<int:group_id>/",
        VenueScheduleGroupDetailView.as_view(),
        name="venue-schedule-group-detail",
    ),
    path(
        "<slug:slug>/schedule-overrides/",
        VenueScheduleOverrideListCreateView.as_view(),
        name="venue-schedule-override-list-create",
    ),
    path(
        "<slug:slug>/schedule-overrides/<int:override_id>/",
        VenueScheduleOverrideDetailView.as_view(),
        name="venue-schedule-override-detail",
    ),
    path("<slug:slug>/", VenueDetailView.as_view(), name="venue-detail"),
]
