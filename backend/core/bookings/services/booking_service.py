from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from bookings.exceptions import (
    InvalidBookingDateError,
    RazorpayOrderCreationError,
    ScheduleUnavailableError,
    SlotAlreadyBookedError,
    SlotLockedError,
    VenueNotAvailableError,
    VenueScheduleNotFoundError,
)
from bookings.models import (
    Booking,
    BookingSession,
    BookingSessionStatus,
    BookingStatus,
    Payment,
    PaymentProvider,
    PaymentStatus,
)
from bookings.services.razorpay_service import RazorpayService
from venues.availability import is_schedule_available_on_date
from venues.models import Venue, VenueSchedule, VenueStatus


@dataclass(frozen=True)
class BookingStartResult:
    booking_session: BookingSession
    payment: Payment
    amount_paise: int
    currency: str
    key: str


class BookingService:
    @staticmethod
    def start_booking(
        *,
        user,
        venue_schedule_id: int,
        booking_date: date,
    ) -> BookingStartResult:
        schedule = BookingService._get_schedule(venue_schedule_id)
        venue = schedule.group.venue

        BookingService._validate_booking_date(booking_date)
        BookingService._validate_venue(venue)
        BookingService._validate_schedule(schedule, booking_date)
        BookingService._ensure_slot_not_booked(schedule, booking_date)
        BookingService._ensure_slot_not_locked(schedule, booking_date)

        locked_price = schedule.price
        expires_at = timezone.now() + settings.BOOKING_LOCK_DURATION

        try:
            with transaction.atomic():
                BookingService._ensure_slot_not_booked(schedule, booking_date)
                BookingService._ensure_slot_not_locked(schedule, booking_date)
                session = BookingSession.objects.create(
                    user=user,
                    venue_schedule=schedule,
                    booking_date=booking_date,
                    status=BookingSessionStatus.ACTIVE,
                    expires_at=expires_at,
                    locked_price=locked_price,
                )
        except IntegrityError as exc:
            raise SlotLockedError(
                "Someone else is currently booking this slot. "
                "Please try again in a few minutes.",
            ) from exc

        amount_paise = BookingService._to_paise(locked_price)

        try:
            order = RazorpayService().create_order(
                amount_paise=amount_paise,
                currency="INR",
                receipt=str(session.id),
            )
        except RazorpayOrderCreationError:
            BookingService._release_session(session)
            raise

        with transaction.atomic():
            payment = Payment.objects.create(
                booking_session=session,
                provider=PaymentProvider.RAZORPAY,
                razorpay_order_id=order["id"],
                amount=locked_price,
                currency="INR",
                status=PaymentStatus.ORDER_CREATED,
                gateway_response=order,
            )

        return BookingStartResult(
            booking_session=session,
            payment=payment,
            amount_paise=amount_paise,
            currency="INR",
            key=settings.RAZORPAY_KEY_ID,
        )

    @staticmethod
    def _get_schedule(venue_schedule_id: int) -> VenueSchedule:
        schedule = (
            VenueSchedule.objects.select_related("group__venue")
            .filter(pk=venue_schedule_id)
            .first()
        )
        if schedule is None:
            raise VenueScheduleNotFoundError("Venue schedule not found.")
        return schedule

    @staticmethod
    def _validate_booking_date(booking_date: date) -> None:
        if booking_date < timezone.localdate():
            raise InvalidBookingDateError("Booking date cannot be in the past.")

    @staticmethod
    def _validate_venue(venue: Venue) -> None:
        if not venue.is_active:
            raise VenueNotAvailableError("This venue is not available for booking.")
        if venue.status != VenueStatus.APPROVED:
            raise VenueNotAvailableError("This venue is not available for booking.")

    @staticmethod
    def _validate_schedule(schedule: VenueSchedule, booking_date: date) -> None:
        if not is_schedule_available_on_date(schedule, booking_date):
            raise ScheduleUnavailableError(
                "This schedule is not available for the selected date.",
            )

    @staticmethod
    def _ensure_slot_not_booked(schedule: VenueSchedule, booking_date: date) -> None:
        if Booking.objects.filter(
            venue_schedule=schedule,
            booking_date=booking_date,
            status=BookingStatus.CONFIRMED,
        ).exists():
            raise SlotAlreadyBookedError("This slot is already booked.")

    @staticmethod
    def _ensure_slot_not_locked(schedule: VenueSchedule, booking_date: date) -> None:
        if BookingSession.objects.filter(
            venue_schedule=schedule,
            booking_date=booking_date,
            status=BookingSessionStatus.ACTIVE,
            expires_at__gt=timezone.now(),
        ).exists():
            raise SlotLockedError(
                "Someone else is currently booking this slot. "
                "Please try again in a few minutes.",
            )

    @staticmethod
    def _release_session(session: BookingSession) -> None:
        session.status = BookingSessionStatus.EXPIRED
        session.lock_released_at = timezone.now()
        session.remarks = "Razorpay order creation failed"
        session.save(
            update_fields=["status", "lock_released_at", "remarks", "updated_at"],
        )

    @staticmethod
    def _to_paise(amount: Decimal) -> int:
        paise = (amount * Decimal("100")).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return int(paise)
