from rest_framework import serializers

from bookings.models import Booking, BookingStatus


class BookingStartSerializer(serializers.Serializer):
    venue_schedule_id = serializers.IntegerField(min_value=1)
    booking_date = serializers.DateField()


class BookingStartResponseSerializer(serializers.Serializer):
    booking_session_id = serializers.UUIDField(source="booking_session.id")
    razorpay_order_id = serializers.CharField(source="payment.razorpay_order_id")
    amount = serializers.IntegerField(source="amount_paise")
    currency = serializers.CharField()
    expires_at = serializers.DateTimeField(source="booking_session.expires_at")
    key = serializers.CharField()


class BookingSerializer(serializers.ModelSerializer):
    venue_id = serializers.IntegerField(
        source="venue_schedule.group.venue_id",
        read_only=True,
    )
    venue_slug = serializers.SlugField(
        source="venue_schedule.group.venue.slug",
        read_only=True,
    )
    venue_name = serializers.CharField(
        source="venue_schedule.group.venue.name",
        read_only=True,
    )
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    start_time = serializers.TimeField(
        source="venue_schedule.start_time",
        read_only=True,
    )
    end_time = serializers.TimeField(
        source="venue_schedule.end_time",
        read_only=True,
    )
    price = serializers.DecimalField(
        source="booking_amount",
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

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
            "confirmed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["status"] = instance.status.lower()
        return data


class BookingStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()

    def validate_status(self, value):
        normalized = value.upper()
        booking = self.context["booking"]

        if booking.status == BookingStatus.CANCELLED:
            raise serializers.ValidationError("Booking is already cancelled.")
        if normalized != BookingStatus.CANCELLED:
            raise serializers.ValidationError("Only cancellation is supported.")
        return BookingStatus.CANCELLED

    def save(self):
        booking = self.context["booking"]
        booking.status = BookingStatus.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        return booking
