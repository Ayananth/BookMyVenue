from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List
from decimal import Decimal

from app.models.venue import (
    BookingType,
)


class VenueStatus(str, Enum):
    APPROVED = "approved"
    PENDING_APPROVAL = "pending_approval"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class ImageUploadResponse(BaseModel):
    public_id: str
    url: str
    secure_url: str
    width: int
    height: int
    format: str
    bytes: int




class VenueImageCreate(BaseModel):
    image_url: str
    is_cover: bool = False
    sort_order: int = 0

class VenueImageResponse(BaseModel):
    id: int
    image_url: str
    is_primary: bool


class VenueCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    category_id: int
    location_id: int

    address: str = Field(..., min_length=5)
    description: str | None = None

    capacity: int = Field(..., gt=0)

    booking_type: BookingType

    contact_name: str = Field(..., min_length=2, max_length=100)
    contact_phone: str = Field(..., min_length=10, max_length=20)
    contact_email: EmailStr

    amenities: list[str] = []

    images: list[VenueImageCreate] = []


class VenueCreateResponse(BaseModel):
    id: int
    name: str
    status: VenueStatus
    created_at: datetime

    model_config = {
        "from_attributes": True
    }



class VenueUpdate(BaseModel):
    category_id: int | None = None
    location_id: int | None = None
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
    )
    description: str | None = None
    address: str | None = None
    capacity: int | None = Field(
        default=None,
        gt=0,
    )
    amenities: list[str] | None = None
    status: VenueStatus | None = None
    is_active: bool | None = None


class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    category_id: int
    location_id: int
    name: str
    description: str | None
    address: str
    capacity: int
    status: VenueStatus
    amenities: list[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VenueListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    capacity: int
    status: VenueStatus
    is_active: bool



class HomePageVenueCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    icon_url: str | None = None


class HomepageVenueResponse(BaseModel):
    id: int
    name: str
    address: str
    capacity: int

    category_id: int
    category: str

    city: str
    district: str
    state: str
    image: str | None = None
    price: Decimal | None
