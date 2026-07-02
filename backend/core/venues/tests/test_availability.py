from datetime import date, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import (
    Booking,
    BookingSession,
    BookingSessionStatus,
    BookingStatus,
    Payment,
    PaymentStatus,
)
from venues.availability import get_available_slots
from venues.models import (
    BookingType,
    City,
    District,
    Venue,
    VenueCategory,
    VenueSchedule,
    VenueScheduleGroup,
    VenueScheduleGroupDay,
    VenueScheduleOverride,
    VenueStatus,
)

User = get_user_model()


def _create_confirmed_booking(user, venue_schedule, booking_date, amount):
    session = BookingSession.objects.create(
        user=user,
        venue_schedule=venue_schedule,
        booking_date=booking_date,
        locked_price=amount,
        status=BookingSessionStatus.COMPLETED,
        expires_at=timezone.now(),
    )
    payment = Payment.objects.create(
        booking_session=session,
        razorpay_order_id=f"order_{session.id}",
        amount=amount,
        status=PaymentStatus.SUCCESS,
    )
    return Booking.objects.create(
        booking_session=session,
        payment=payment,
        user=user,
        venue_schedule=venue_schedule,
        booking_date=booking_date,
        booking_amount=amount,
        status=BookingStatus.CONFIRMED,
        confirmed_at=timezone.now(),
    )


class AvailabilityTestCase(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="password123",
            role="venue",
        )
        self.category = VenueCategory.objects.create(name="Hall")
        self.district = District.objects.create(name="Andheri")
        self.city = City.objects.create(district=self.district, name="Mumbai")
        self.venue = Venue.objects.create(
            owner=self.owner,
            category=self.category,
            city=self.city,
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
        customer = User.objects.create_user(
            email="customer@example.com",
            password="password123",
        )
        _create_confirmed_booking(
            customer,
            self.morning_slot,
            self.target_date,
            Decimal("1000.00"),
        )

        result = get_available_slots(self.venue, self.target_date)

        self.assertEqual(len(result["slots"]), 1)
        self.assertEqual(result["slots"][0]["name"], "Afternoon")

    def test_ignores_cancelled_bookings(self):
        customer = User.objects.create_user(
            email="customer@example.com",
            password="password123",
        )
        session = BookingSession.objects.create(
            user=customer,
            venue_schedule=self.morning_slot,
            booking_date=self.target_date,
            locked_price=Decimal("1000.00"),
            status=BookingSessionStatus.COMPLETED,
            expires_at=timezone.now(),
        )
        payment = Payment.objects.create(
            booking_session=session,
            razorpay_order_id=f"order_{session.id}",
            amount=Decimal("1000.00"),
            status=PaymentStatus.SUCCESS,
        )
        Booking.objects.create(
            booking_session=session,
            payment=payment,
            user=customer,
            venue_schedule=self.morning_slot,
            booking_date=self.target_date,
            booking_amount=Decimal("1000.00"),
            status=BookingStatus.CANCELLED,
            confirmed_at=timezone.now(),
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
        self.district = District.objects.create(name="Andheri")
        self.city = City.objects.create(district=self.district, name="Mumbai")
        self.venue = Venue.objects.create(
            owner=self.owner,
            category=self.category,
            city=self.city,
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
