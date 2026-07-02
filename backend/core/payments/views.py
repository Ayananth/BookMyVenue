from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.exceptions import (
    BookingError,
    BookingSessionExpiredError,
    BookingSessionNotActiveError,
    BookingSessionNotFoundError,
    InvalidPaymentSignatureError,
    InvalidPaymentStatusError,
    PaymentAlreadyProcessedError,
    PaymentNotFoundError,
    PaymentNotSuccessfulError,
    SlotAlreadyBookedError,
)
from bookings.models import BookingSession
from bookings.services.payment_service import PaymentService

from payments.serializers import (
    PaymentVerificationResponseSerializer,
    PaymentVerificationSerializer,
)

PAYMENT_ERROR_STATUS = {
    BookingSessionNotFoundError: status.HTTP_404_NOT_FOUND,
    PaymentNotFoundError: status.HTTP_404_NOT_FOUND,
    BookingSessionExpiredError: status.HTTP_400_BAD_REQUEST,
    BookingSessionNotActiveError: status.HTTP_400_BAD_REQUEST,
    InvalidPaymentSignatureError: status.HTTP_400_BAD_REQUEST,
    InvalidPaymentStatusError: status.HTTP_400_BAD_REQUEST,
    PaymentNotSuccessfulError: status.HTTP_400_BAD_REQUEST,
    PaymentAlreadyProcessedError: status.HTTP_409_CONFLICT,
    SlotAlreadyBookedError: status.HTTP_409_CONFLICT,
}


class PaymentVerifyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PaymentVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        session_exists = BookingSession.objects.filter(
            pk=validated["booking_session_id"],
            user=request.user,
        ).exists()
        if not session_exists:
            return Response(
                {"message": "Booking session not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            booking = PaymentService.verify_payment(
                booking_session_id=validated["booking_session_id"],
                razorpay_order_id=validated["razorpay_order_id"],
                razorpay_payment_id=validated["razorpay_payment_id"],
                razorpay_signature=validated["razorpay_signature"],
            )
        except BookingError as exc:
            return Response(
                {"message": exc.message},
                status=PAYMENT_ERROR_STATUS.get(
                    type(exc),
                    status.HTTP_400_BAD_REQUEST,
                ),
            )

        response_serializer = PaymentVerificationResponseSerializer(booking)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
