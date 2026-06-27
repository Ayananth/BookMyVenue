from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from bookings.models import Booking, BookingStatus
from venues.availability import get_available_slots
from venues.models import (
    BookingType,
    Location,
    Venue,
    VenueCategory,
    VenueSchedule,
    VenueScheduleGroup,
    VenueScheduleGroupDay,
    VenueScheduleOverride,
    VenueStatus,
)

User = get_user_model()


class AvailabilityTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="password123",
            role="venue",
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
            name="Test Venue",
            slug="test-venue",
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
        self.target_date = date(2026, 6, 29)

    def test_returns_slots_for_matching_weekday_group(self):
        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(result["date"], "2026-06-29")
        self.assertEqual(result["day_of_week"], 0)
        self.assertEqual(result["schedule_group"]["name"], "Weekdays")
        self.assertEqual(len(result["slots"]), 2)
        self.assertEqual(result["slots"][0]["name"], "Morning")

    def test_returns_empty_when_no_weekday_group_matches(self):
        result = get_available_slots(self.venue, date(2026, 7, 4))

        self.assertEqual(result["day_of_week"], 5)
        self.assertIsNone(result["schedule_group"])
        self.assertEqual(result["slots"], [])

    def test_excludes_slots_marked_unavailable_in_schedule(self):
        self.morning_slot.is_available = False
        self.morning_slot.save()

        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(len(result["slots"]), 1)
        self.assertEqual(result["slots"][0]["name"], "Afternoon")

    def test_excludes_slots_blocked_by_full_day_override(self):
        VenueScheduleOverride.objects.create(
            venue=self.venue,
            override_date=self.target_date,
            start_time=None,
            end_time=None,
            is_available=False,
            reason="Closed",
        )

        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(result["slots"], [])

    def test_excludes_slots_blocked_by_partial_override(self):
        VenueScheduleOverride.objects.create(
            venue=self.venue,
            override_date=self.target_date,
            start_time=time(8, 0),
            end_time=time(13, 0),
            is_available=False,
            reason="Maintenance",
        )

        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(len(result["slots"]), 1)
        self.assertEqual(result["slots"][0]["name"], "Afternoon")

    def test_excludes_slots_blocked_by_booking(self):
        Booking.objects.create(
            venue=self.venue,
            user=None,
            booking_date=self.target_date,
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.CONFIRMED,
        )

        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(len(result["slots"]), 1)
        self.assertEqual(result["slots"][0]["name"], "Afternoon")

    def test_ignores_cancelled_bookings(self):
        Booking.objects.create(
            venue=self.venue,
            user=None,
            booking_date=self.target_date,
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            status=BookingStatus.CANCELLED,
        )

        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(len(result["slots"]), 2)


class VenueAvailabilityAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="password123",
            role="venue",
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
        VenueSchedule.objects.create(
            group=self.group,
            name="Morning",
            start_time=time(9, 0),
            end_time=time(12, 0),
            price=Decimal("1000.00"),
            is_available=True,
        )

    def test_availability_endpoint_returns_slots(self):
        response = self.client.get(
            "/venues/api-venue/availability/",
            {"date": "2026-06-29"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["venue_slug"], "api-venue")
        self.assertEqual(len(response.data["slots"]), 1)

    def test_availability_endpoint_requires_date(self):
        response = self.client.get("/venues/api-venue/availability/")

        self.assertEqual(response.status_code, 400)
        self.assertIn("date", response.data["detail"].lower())

    def test_availability_endpoint_rejects_invalid_date(self):
        response = self.client.get(
            "/venues/api-venue/availability/",
            {"date": "not-a-date"},
        )

        self.assertEqual(response.status_code, 400)
