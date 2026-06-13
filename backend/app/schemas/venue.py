from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal


class VenueStatus(str, Enum):
    APPROVED = "approved"
    PENDING_APPROVAL = "pending_approval"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class VenueCreate(BaseModel):
    category_id: int
    location_id: int
    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = None
    address: str
    capacity: int = Field(..., gt=0)
    amenities: list[str] = []


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
