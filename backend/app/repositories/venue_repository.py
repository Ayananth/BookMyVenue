# repositories/venue_repository.py

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Venue, VenueStatus


async def get_homepage_venues(
    db: AsyncSession,
    limit: int = 6,
) -> list[Venue]:
    ranked_subquery = (
        select(
            Venue.id.label("venue_id"),
            Venue.category_id,
            func.row_number()
            .over(
                partition_by=Venue.category_id,
                order_by=Venue.id,
            )
            .label("rn"),
        )
        .where(
            Venue.is_active.is_(True),
            Venue.status == VenueStatus.APPROVED,
        )
        .subquery()
    )

    result = await db.execute(
        select(Venue)
        .join(
            ranked_subquery,
            Venue.id == ranked_subquery.c.venue_id,
        )
        .where(ranked_subquery.c.rn == 1)
        .order_by(Venue.id)
        .limit(limit)
    )

    venues = result.scalars().all()

    if len(venues) < limit:
        selected_ids = [venue.id for venue in venues]

        result = await db.execute(
            select(Venue)
            .where(
                Venue.is_active.is_(True),
                Venue.status == VenueStatus.APPROVED,
                Venue.id.not_in(selected_ids)
                if selected_ids
                else True,
            )
            .order_by(Venue.id)
            .limit(limit - len(venues))
        )

        venues.extend(result.scalars().all())

    return venues