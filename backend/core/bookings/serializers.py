from rest_framework import serializers

from bookings.models import Booking, BookingStatus, Payment
from venues.models import Venue, VenueSchedule
from venues.serializers import CitySerializer, VenueCategorySerializer


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


class BookingListVenueSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = Venue
        fields = ("id", "slug", "name", "address", "city")
        read_only_fields = fields


class BookingListScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueSchedule
        fields = ("id", "name", "start_time", "end_time", "price", "is_available")
        read_only_fields = fields


class BookingListPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ("id", "provider", "status", "amount", "currency", "verified_at")
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["provider"] = instance.provider.lower()
        data["status"] = instance.status.lower()
        return data


class BookingListSerializer(serializers.ModelSerializer):
    venue = BookingListVenueSerializer(
        source="venue_schedule.group.venue",
        read_only=True,
    )
    schedule = BookingListScheduleSerializer(
        source="venue_schedule",
        read_only=True,
    )
    payment = BookingListPaymentSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "booking_date",
            "booking_amount",
            "status",
            "confirmed_at",
            "cancelled_at",
            "created_at",
            "venue",
            "schedule",
            "payment",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["status"] = instance.status.lower()
        return data


class BookingDetailVenueSerializer(serializers.ModelSerializer):
    category = VenueCategorySerializer(read_only=True)
    city = CitySerializer(read_only=True)

    class Meta:
        model = Venue
        fields = (
            "id",
            "slug",
            "name",
            "address",
            "capacity",
            "booking_type",
            "category",
            "city",
        )
        read_only_fields = fields


class BookingDetailScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueSchedule
        fields = ("id", "name", "start_time", "end_time", "price", "is_available")
        read_only_fields = fields


class BookingDetailPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "provider",
            "status",
            "amount",
            "currency",
            "razorpay_order_id",
            "verified_at",
            "created_at",
        )
        read_only_fields = fields

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["provider"] = instance.provider.lower()
        data["status"] = instance.status.lower()
        return data


class BookingDetailSerializer(serializers.ModelSerializer):
    venue = BookingDetailVenueSerializer(
        source="venue_schedule.group.venue",
        read_only=True,
    )
    schedule = BookingDetailScheduleSerializer(
        source="venue_schedule",
        read_only=True,
    )
    payment = BookingDetailPaymentSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
            "booking_date",
            "booking_amount",
            "status",
            "confirmed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
            "venue",
            "schedule",
            "payment",
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
