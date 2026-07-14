from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rating import Rating


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _venue_ratings_query(self, venue_id: int) -> Select[tuple[Rating]]:
        return (
            select(Rating)
            .options(selectinload(Rating.review))
            .where(Rating.venue_id == venue_id)
            .order_by(Rating.created_at.desc())
        )

    async def list_by_venue(
        self,
        venue_id: int,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Rating]:
        result = await self.db.execute(
            self._venue_ratings_query(venue_id).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_venue(self, venue_id: int) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Rating)
            .where(Rating.venue_id == venue_id)
        )
        return int(result.scalar_one())

    async def average_rating_by_venue(self, venue_id: int) -> float | None:
        result = await self.db.execute(
            select(func.avg(Rating.rating)).where(Rating.venue_id == venue_id)
        )
        average = result.scalar_one()
        return float(average) if average is not None else None
