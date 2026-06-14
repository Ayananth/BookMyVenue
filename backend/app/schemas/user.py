from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import UserRole


class UserCreate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str | None
    email: str | None
    phone: str | None
    avatar_url: str | None
    role: UserRole
    is_active: bool
    is_blocked: bool
    is_email_verified: bool
    is_phone_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoogleAuthRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
