from uuid import UUID

import razorpay
from django.db import transaction
from django.utils import timezone

from bookings.exceptions import (
    BookingSessionNotFoundError,
    InvalidPaymentSignatureError,
    InvalidPaymentStatusError,
    PaymentAlreadyProcessedError,
    PaymentNotFoundError,
)
from bookings.models import Booking, BookingSession, Payment, PaymentStatus
from bookings.services.booking_service import BookingService
from bookings.services.razorpay_service import RazorpayService


class PaymentService:
    @staticmethod
    def verify_payment(
        booking_session_id: UUID,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> Booking:
        session = (
            BookingSession.objects.select_related("payment")
            .filter(pk=booking_session_id)
            .first()
        )
        if session is None:
            raise BookingSessionNotFoundError("Booking session not found.")

        try:
            payment = session.payment
        except Payment.DoesNotExist as exc:
            raise PaymentNotFoundError(
                "Payment not found for this booking session.",
            ) from exc

        PaymentService._validate_payment_status(payment)

        PaymentService._verify_razorpay_signature(
            razorpay_order_id=razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
        )

        with transaction.atomic():
            payment = Payment.objects.select_for_update().get(pk=payment.pk)
            PaymentService._validate_payment_status(payment)

            now = timezone.now()
            payment.status = PaymentStatus.SUCCESS
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.verified_at = now
            payment.save(
                update_fields=[
                    "status",
                    "razorpay_payment_id",
                    "razorpay_signature",
                    "verified_at",
                    "updated_at",
                ],
            )

            return BookingService.complete_booking(session.id)

    @staticmethod
    def _validate_payment_status(payment: Payment) -> None:
        if payment.status == PaymentStatus.SUCCESS:
            raise PaymentAlreadyProcessedError(
                "Payment has already been processed.",
            )
        if payment.status != PaymentStatus.ORDER_CREATED:
            raise InvalidPaymentStatusError(
                "Payment is not in a verifiable state.",
            )

    @staticmethod
    def _verify_razorpay_signature(
        *,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
    ) -> None:
        client = RazorpayService().client
        try:
            client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                },
            )
        except razorpay.errors.SignatureVerificationError as exc:
            raise InvalidPaymentSignatureError(
                "Payment signature verification failed.",
            ) from exc
