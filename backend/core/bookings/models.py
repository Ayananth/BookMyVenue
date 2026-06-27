from django.conf import settings
from django.db import models
from django.db.models import F, Q

from venues.models import Venue


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"


class Booking(models.Model):
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="bookings",
        blank=True,
        null=True,
    )
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BookingStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "bookings"
        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F("start_time")),
                name="ck_booking_time_range",
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="ck_booking_price",
            ),
        ]
        indexes = [
            models.Index(fields=["venue"], name="ix_bookings_venue_id"),
            models.Index(fields=["user"], name="ix_bookings_user_id"),
            models.Index(fields=["booking_date"], name="ix_bookings_date"),
        ]

    def __str__(self) -> str:
        return f"Booking #{self.pk} - {self.venue.name}"
