from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rating import Rating
from app.repositories.review import ReviewRepository
from app.schemas.review import VenueReviewItem, VenueReviewsResponse


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ReviewRepository(db)

    def _to_item(self, rating: Rating) -> VenueReviewItem:
        review = rating.review
        # Hidden reviews are omitted from the payload; the rating still shows.
        if review is not None and review.is_hidden:
            review = None

        return VenueReviewItem(
            rating_id=rating.id,
            user_id=rating.user_id,
            booking_id=rating.booking_id,
            rating=rating.rating,
            review_id=review.id if review else None,
            title=review.title if review else None,
            review=review.review if review else None,
            is_edited=review.is_edited if review else None,
            created_at=rating.created_at,
        )

    async def list_venue_reviews(
        self,
        venue_id: int,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> VenueReviewsResponse:
        ratings = await self.repo.list_by_venue(venue_id, skip=skip, limit=limit)
        total_count = await self.repo.count_by_venue(venue_id)
        average_rating = await self.repo.average_rating_by_venue(venue_id)

        return VenueReviewsResponse(
            venue_id=venue_id,
            average_rating=(
                round(average_rating, 2) if average_rating is not None else None
            ),
            total_count=total_count,
            items=[self._to_item(rating) for rating in ratings],
        )
