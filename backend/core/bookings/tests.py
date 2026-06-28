from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.security import create_access_token
from bookings.models import Booking, BookingStatus
from venues.models import (
    BookingType,
    Location,
    Venue,
    VenueCategory,
    VenueSchedule,
    VenueScheduleGroup,
    VenueScheduleGroupDay,
    VenueStatus,
)

User = get_user_model()


class BookingAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="password123",
            role="venue",
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            role="user",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password123",
            role="user",
        )
        self.category = VenueCategory.objects.create(name="Hall")
        self.location = Location.objects.create(
            city="Mumbai",
            district="Andheri",
            state="Maharashtra",
        )
        self.venue = Venue.objects.create(
            owner=self.owner,
            category=self.category,
            location=self.location,
            name="API Venue",
            slug="api-venue",
            address="123 Test St",
            capacity=100,
            contact_name="Owner",
            contact_phone="9999999999",
            contact_email="owner@example.com",
            status=VenueStatus.APPROVED,
            booking_type=BookingType.HOURLY,
        )
        self.group = VenueScheduleGroup.objects.create(
            venue=self.venue,
            name="Weekdays",
            is_active=True,
        )
        VenueScheduleGroupDay.objects.create(group=self.group, day_of_week=0)
        self.morning_slot = VenueSchedule.objects.create(
            group=self.group,
            name="Morning",
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            is_available=True,
        )
        self.afternoon_slot = VenueSchedule.objects.create(
            group=self.group,
            name="Afternoon",
            start_time=time(13, 0),
            end_time=time(17, 0),
            price=Decimal("1500.00"),
            is_available=True,
        )
        self.booking_date = "2026-06-29"
        self.user_token = create_access_token(self.user.id)
        self.owner_token = create_access_token(self.owner.id)

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_booking_requires_authentication(self):
        response = self.client.post(
            "/bookings/",
            {
                "venue_slug": self.venue.slug,
                "booking_date": self.booking_date,
                "schedule_ids": [self.morning_slot.id],
            },
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))

    def test_create_booking_for_available_slot(self):
        self._auth(self.user_token)
        response = self.client.post(
            "/bookings/",
            {
                "venue_slug": self.venue.slug,
                "booking_date": self.booking_date,
                "schedule_ids": [self.morning_slot.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["venue_slug"], "api-venue")
        self.assertEqual(response.data[0]["status"], BookingStatus.PENDING)
        self.assertEqual(response.data[0]["price"], "1000.00")
        self.assertEqual(Booking.objects.count(), 1)

    def test_create_multiple_bookings_in_one_request(self):
        self._auth(self.user_token)
        response = self.client.post(
            "/bookings/",
            {
                "venue_slug": self.venue.slug,
                "booking_date": self.booking_date,
                "schedule_ids": [self.morning_slot.id, self.afternoon_slot.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(Booking.objects.count(), 2)

    def test_rejects_unavailable_slot(self):
        Booking.objects.create(
            venue=self.venue,
            user=self.other_user,
            booking_date=date(2026, 6, 29),
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.CONFIRMED,
        )

        self._auth(self.user_token)
        response = self.client.post(
            "/bookings/",
            {
                "venue_slug": self.venue.slug,
                "booking_date": self.booking_date,
                "schedule_ids": [self.morning_slot.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("schedule_ids", response.data)

    def test_user_can_list_own_bookings(self):
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            booking_date=date(2026, 6, 29),
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.PENDING,
        )
        Booking.objects.create(
            venue=self.venue,
            user=self.other_user,
            booking_date=date(2026, 6, 29),
            start_time=time(13, 0),
            end_time=time(17, 0),
            price=Decimal("1500.00"),
            status=BookingStatus.PENDING,
        )

        self._auth(self.user_token)
        response = self.client.get("/bookings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], booking.id)

    def test_venue_owner_can_list_venue_bookings(self):
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            booking_date=date(2026, 6, 29),
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.PENDING,
        )

        self._auth(self.owner_token)
        response = self.client.get("/bookings/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], booking.id)

    def test_cancel_booking(self):
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            booking_date=date(2026, 6, 29),
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.PENDING,
        )

        self._auth(self.user_token)
        response = self.client.patch(
            f"/bookings/{booking.id}/",
            {"status": BookingStatus.CANCELLED},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], BookingStatus.CANCELLED)

    def test_other_user_cannot_access_booking(self):
        booking = Booking.objects.create(
            venue=self.venue,
            user=self.user,
            booking_date=date(2026, 6, 29),
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.PENDING,
        )

        other_token = create_access_token(self.other_user.id)
        self._auth(other_token)
        response = self.client.get(f"/bookings/{booking.id}/")

        self.assertEqual(response.status_code, 403)
