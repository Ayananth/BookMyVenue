import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return f"{salt}${derived_key.hex()}"


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def verify_google_token(token: str) -> dict | None:
    if not settings.google_client_id:
        return None

    try:
        return id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.google_client_id,
        )
    except Exception:
        return None
