from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Location,
    Venue,
    VenueCategory,
    VenueSlot,
    VenueStatus,
)

HOMEPAGE_VENUE_LIMIT = 12


async def get_homepage_venues(db: AsyncSession) -> Sequence[RowMapping]:
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
        select(
            Venue.id,
            Venue.name,
            Venue.address,
            Venue.capacity,

            VenueCategory.name.label("category"),

            Location.city.label("city"),
            Location.district.label("district"),
            Location.state.label("state"),

            func.min(VenueSlot.price).label("price"),
        )
        .join(
            ranked_subquery,
            Venue.id == ranked_subquery.c.venue_id,
        )
        .join(
            VenueCategory,
            Venue.category_id == VenueCategory.id,
        )
        .join(
            Location,
            Venue.location_id == Location.id,
        )
        .outerjoin(
            VenueSlot,
            Venue.id == VenueSlot.venue_id,
        )
        .where(
            ranked_subquery.c.rn == 1,
        )
        .group_by(
            Venue.id,
            Venue.name,
            Venue.address,
            Venue.capacity,
            VenueCategory.name,
            Location.city,
            Location.district,
            Location.state,
        )
        .order_by(VenueCategory.name)
        .limit(HOMEPAGE_VENUE_LIMIT)
    )

    return result.mappings().all()
