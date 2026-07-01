from django.urls import reverse

from accounts.models import User
from bookings.models import Booking, BookingStatus
from venues.models import Venue, VenueStatus


def get_dashboard_stats() -> list[dict]:
    pending_venues = Venue.objects.filter(status=VenueStatus.PENDING_APPROVAL).count()
    approved_venues = Venue.objects.filter(status=VenueStatus.APPROVED).count()
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status=BookingStatus.PENDING).count()
    confirmed_bookings = Booking.objects.filter(status=BookingStatus.CONFIRMED).count()
    total_users = User.objects.count()

    venue_changelist = reverse("admin:venues_venue_changelist")
    booking_changelist = reverse("admin:bookings_booking_changelist")
    user_changelist = reverse("admin:accounts_user_changelist")

    return [
        {
            "label": "Pending Venues",
            "value": pending_venues,
            "icon": "fas fa-hourglass-half",
            "color": "warning",
            "url": f"{venue_changelist}?status__exact=pending_approval",
        },
        {
            "label": "Approved Venues",
            "value": approved_venues,
            "icon": "fas fa-building",
            "color": "success",
            "url": f"{venue_changelist}?status__exact=approved",
        },
        {
            "label": "Pending Bookings",
            "value": pending_bookings,
            "icon": "fas fa-clock",
            "color": "info",
            "url": f"{booking_changelist}?status__exact=pending",
        },
        {
            "label": "Confirmed Bookings",
            "value": confirmed_bookings,
            "icon": "fas fa-calendar-check",
            "color": "primary",
            "url": f"{booking_changelist}?status__exact=confirmed",
        },
        {
            "label": "Total Bookings",
            "value": total_bookings,
            "icon": "fas fa-ticket-alt",
            "color": "secondary",
            "url": booking_changelist,
        },
        {
            "label": "Total Users",
            "value": total_users,
            "icon": "fas fa-users",
            "color": "dark",
            "url": user_changelist,
        },
    ]
