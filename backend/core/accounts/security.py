import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return f"{salt}${derived_key.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, stored_key = password_hash.split("$", 1)
    except ValueError:
        return False

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    )
    return secrets.compare_digest(derived_key.hex(), stored_key)
