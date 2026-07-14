from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.review import VenueReviewsResponse
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
