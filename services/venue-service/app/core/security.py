import jwt

from app.core.config import settings


def decode_access_token(token: str) -> int | None:
    """Decode a Django-compatible access JWT and return the user id."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") not in (None, "access"):
            return None
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        return None
