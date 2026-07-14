from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rating import Rating
from app.repositories.review import ReviewRepository
from app.schemas.review import (
    VenueReviewCreate,
    VenueReviewItem,
    VenueReviewsResponse,
)


class ReviewService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
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

    async def create_venue_review(
        self,
        *,
        venue_id: int,
        user_id: int,
        payload: VenueReviewCreate,
    ) -> VenueReviewItem:
        if payload.title and not payload.review:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Review text is required when a title is provided.",
            )

        existing = await self.repo.get_by_user_and_venue(
            user_id=user_id,
            venue_id=venue_id,
        )
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already rated this venue.",
            )

        try:
            rating = await self.repo.create_rating(
                venue_id=venue_id,
                user_id=user_id,
                rating_value=payload.rating,
                booking_id=payload.booking_id,
            )

            if payload.review:
                await self.repo.create_review(
                    rating_id=rating.id,
                    title=payload.title,
                    review_text=payload.review,
                )

            await self.db.refresh(rating, attribute_names=["review"])
        except IntegrityError as exc:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already rated this venue, or this booking already has a rating.",
            ) from exc

        return self._to_item(rating)
