from rest_framework import serializers

from bookings.models import Booking


class PaymentVerificationSerializer(serializers.Serializer):
    booking_session_id = serializers.UUIDField()
    razorpay_order_id = serializers.CharField(max_length=255, trim_whitespace=True)
    razorpay_payment_id = serializers.CharField(max_length=255, trim_whitespace=True)
    razorpay_signature = serializers.CharField(max_length=512, trim_whitespace=True)

    def validate_razorpay_order_id(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate_razorpay_payment_id(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def validate_razorpay_signature(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value


class PaymentVerificationResponseSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField(source="id")
    status = serializers.CharField()
    message = serializers.SerializerMethodField()

    def get_message(self, obj: Booking) -> str:
        return "Booking confirmed successfully."
