from datetime import date

from django.db import transaction
from rest_framework import serializers

from bookings.models import Booking, BookingStatus
from venues.availability import get_available_slots
from venues.models import Venue, VenueSchedule, VenueStatus


class BookingSerializer(serializers.ModelSerializer):
    venue_slug = serializers.SlugField(source="venue.slug", read_only=True)
    venue_name = serializers.CharField(source="venue.name", read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True, allow_null=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "venue_id",
            "venue_slug",
            "venue_name",
            "user_id",
            "booking_date",
            "start_time",
            "end_time",
            "price",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class BookingCreateSerializer(serializers.Serializer):
    venue_slug = serializers.SlugField()
    booking_date = serializers.DateField()
    schedule_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )

    def validate_booking_date(self, value: date) -> date:
        if value < date.today():
            raise serializers.ValidationError("Booking date cannot be in the past.")
        return value

    def validate(self, attrs):
        venue = Venue.objects.filter(
            slug=attrs["venue_slug"],
            is_active=True,
            status=VenueStatus.APPROVED,
        ).first()
        if venue is None:
            raise serializers.ValidationError(
                {"venue_slug": "Venue not found or not available for booking."},
            )

        schedule_ids = list(dict.fromkeys(attrs["schedule_ids"]))
        attrs["schedule_ids"] = schedule_ids

        availability = get_available_slots(venue, attrs["booking_date"])
        available_ids = {slot["id"] for slot in availability["slots"]}

        schedules = []
        for schedule_id in schedule_ids:
            if schedule_id not in available_ids:
                raise serializers.ValidationError(
                    {
                        "schedule_ids": (
                            f"Schedule {schedule_id} is not available "
                            "for the selected date."
                        ),
                    },
                )

            schedule = VenueSchedule.objects.select_related("group").get(
                pk=schedule_id,
                group__venue=venue,
                group__is_active=True,
                is_available=True,
            )
            schedules.append(schedule)

        attrs["venue"] = venue
        attrs["schedules"] = schedules
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        bookings = []

        for schedule in validated_data["schedules"]:
            booking = Booking.objects.create(
                venue=validated_data["venue"],
                user=user,
                booking_date=validated_data["booking_date"],
                start_time=schedule.start_time,
                end_time=schedule.end_time,
                price=schedule.price,
                status=BookingStatus.PENDING,
            )
            bookings.append(booking)

        return bookings


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[BookingStatus.CANCELLED])

    def validate_status(self, value):
        booking = self.context["booking"]
        if booking.status == BookingStatus.CANCELLED:
            raise serializers.ValidationError("Booking is already cancelled.")
        if value != BookingStatus.CANCELLED:
            raise serializers.ValidationError("Only cancellation is supported.")
        return value

    def save(self):
        booking = self.context["booking"]
        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        return booking
