from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]

DEFAULT_CORS_ORIGIN_REGEX = (
    r"https?://"
    r"(localhost|127\.0\.0\.1|\[::1\]|"
    r"192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})"
    r"(:\d+)?"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost/bmw"
    static_dir: Path = BASE_DIR / "static"
    media_dir: Path = BASE_DIR / "media"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    google_client_id: str = ""

    cloudinary_cloud_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    cors_origins: list[str] = []
    cors_origin_regex: str | None = DEFAULT_CORS_ORIGIN_REGEX

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            if not value.strip():
                return []
            return [
                origin.strip()
                for origin in value.split(",")
                if origin.strip()
            ]
        return value

    @field_validator("cors_origin_regex", mode="before")
    @classmethod
    def parse_cors_origin_regex(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            return None
        return value


settings = Settings()
