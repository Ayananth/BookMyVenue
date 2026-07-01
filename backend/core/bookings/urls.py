from django.urls import path

from bookings.views import BookingDetailView, BookingListCreateView

urlpatterns = [
    path("", BookingListCreateView.as_view(), name="booking-list-create"),
    path("<int:booking_id>/", BookingDetailView.as_view(), name="booking-detail"),
]
