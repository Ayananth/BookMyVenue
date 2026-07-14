from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.schemas.review import (
    VenueReviewCreate,
    VenueReviewItem,
    VenueReviewsResponse,
)
from app.services.review import ReviewService

router = APIRouter(prefix="/venues", tags=["Reviews"])


@router.get("/{venue_id}/reviews", response_model=VenueReviewsResponse)
async def list_venue_reviews(
    venue_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> VenueReviewsResponse:
    """List ratings and reviews for a venue."""
    return await ReviewService(db).list_venue_reviews(
        venue_id,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{venue_id}/reviews",
    response_model=VenueReviewItem,
    status_code=status.HTTP_201_CREATED,
)
async def create_venue_review(
    venue_id: int,
    payload: VenueReviewCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> VenueReviewItem:
    """Create a rating (and optional review text) for a venue. Requires login."""
    return await ReviewService(db).create_venue_review(
        venue_id=venue_id,
        user_id=user_id,
        payload=payload,
    )
