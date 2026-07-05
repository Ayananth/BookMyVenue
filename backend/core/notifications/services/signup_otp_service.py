from django.conf import settings

from notifications.services.email_service import EmailService
from notifications.services.otp_service import OtpPurpose, OtpService
from notifications.tasks import send_otp_verification_email


class SignupOtpService:
    @staticmethod
    def send_email_otp(email: str, *, async_send: bool = True) -> None:
        normalized_email = email.strip().lower()
        otp = OtpService.create(
            purpose=OtpPurpose.EMAIL_SIGNUP,
            destination=normalized_email,
        )

        if async_send:
            send_otp_verification_email.delay(
                to=normalized_email,
                otp=otp,
                purpose_label="account registration",
            )
            return

        EmailService.send(
            template_key="otp_verification",
            to=normalized_email,
            context={
                "otp_code": otp,
                "purpose_label": "account registration",
                "expires_minutes": settings.OTP_EXPIRE_MINUTES,
            },
        )

    @staticmethod
    def verify_email_otp(email: str, otp: str) -> bool:
        return OtpService.verify(
            purpose=OtpPurpose.EMAIL_SIGNUP,
            destination=email.strip().lower(),
            otp=otp,
        )
