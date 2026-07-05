import logging

from celery import shared_task
from django.conf import settings

from notifications.services.email_service import EmailService

logger = logging.getLogger(__name__)


@shared_task(name="send_otp_verification_email")
def send_otp_verification_email(
    *,
    to: str,
    otp: str,
    purpose_label: str = "verification",
) -> int:
    sent_count = EmailService.send(
        template_key="otp_verification",
        to=to,
        context={
            "otp_code": otp,
            "purpose_label": purpose_label,
            "expires_minutes": settings.OTP_EXPIRE_MINUTES,
        },
    )
    logger.info("Queued OTP verification email delivered to %s.", to)
    return sent_count
