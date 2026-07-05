import json
from enum import Enum

from django.conf import settings

from accounts.security import generate_otp, hash_otp, verify_otp
from notifications.services.redis_client import get_redis_client


class OtpPurpose(str, Enum):
    EMAIL_SIGNUP = "email_signup"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"


class OtpService:
    KEY_PREFIX = "bookmyvenue:otp"

    @classmethod
    def _redis_key(cls, purpose: OtpPurpose | str, destination: str) -> str:
        normalized_destination = destination.strip().lower()
        return f"{cls.KEY_PREFIX}:{purpose}:{normalized_destination}"

    @classmethod
    def _cooldown_key(cls, purpose: OtpPurpose | str, destination: str) -> str:
        return f"{cls._redis_key(purpose, destination)}:cooldown"

    @classmethod
    def create(
        cls,
        *,
        purpose: OtpPurpose | str,
        destination: str,
        length: int | None = None,
    ) -> str:
        client = get_redis_client()
        cooldown_key = cls._cooldown_key(purpose, destination)

        if client.exists(cooldown_key):
            raise OtpResendCooldownError(
                "Please wait before requesting another verification code.",
            )

        otp = generate_otp(length or settings.OTP_LENGTH)
        payload = {
            "otp_hash": hash_otp(otp),
            "attempts": 0,
        }

        ttl_seconds = settings.OTP_EXPIRE_MINUTES * 60
        redis_key = cls._redis_key(purpose, destination)
        client.setex(redis_key, ttl_seconds, json.dumps(payload))
        client.setex(cooldown_key, settings.OTP_RESEND_COOLDOWN_SECONDS, "1")
        return otp

    @classmethod
    def verify(
        cls,
        *,
        purpose: OtpPurpose | str,
        destination: str,
        otp: str,
    ) -> bool:
        client = get_redis_client()
        redis_key = cls._redis_key(purpose, destination)
        raw_payload = client.get(redis_key)

        if not raw_payload:
            return False

        payload = json.loads(raw_payload)
        attempts = payload.get("attempts", 0)

        if attempts >= settings.OTP_MAX_ATTEMPTS:
            client.delete(redis_key)
            raise OtpMaxAttemptsExceededError(
                "Too many invalid attempts. Please request a new verification code.",
            )

        if not verify_otp(otp, payload["otp_hash"]):
            payload["attempts"] = attempts + 1
            remaining_ttl = client.ttl(redis_key)
            if remaining_ttl > 0:
                client.setex(redis_key, remaining_ttl, json.dumps(payload))
            return False

        client.delete(redis_key)
        client.delete(cls._cooldown_key(purpose, destination))
        return True

    @classmethod
    def delete(cls, *, purpose: OtpPurpose | str, destination: str) -> None:
        client = get_redis_client()
        client.delete(cls._redis_key(purpose, destination))
        client.delete(cls._cooldown_key(purpose, destination))


class OtpError(Exception):
    pass


class OtpResendCooldownError(OtpError):
    pass


class OtpMaxAttemptsExceededError(OtpError):
    pass
