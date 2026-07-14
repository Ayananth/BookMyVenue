from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VenueReviewItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rating_id: UUID
    user_id: int
    booking_id: UUID
    rating: int
    review_id: UUID | None = None
    title: str | None = None
    review: str | None = None
    is_edited: bool | None = None
    created_at: datetime


class VenueReviewsResponse(BaseModel):
    venue_id: int
    average_rating: float | None
    total_count: int
    items: list[VenueReviewItem]
