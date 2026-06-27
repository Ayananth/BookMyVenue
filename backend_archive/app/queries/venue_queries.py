from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.engine import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Subquery

from app.models import (
    Location,
    Venue,
    VenueCategory,
    VenueImage,
    VenueSlot,
    VenueStatus,
)
from app.schemas.venue import VenueCreate

HOMEPAGE_VENUE_LIMIT = 12
EXPLORE_VENUE_DEFAULT_LIMIT = 12
EXPLORE_VENUE_MAX_LIMIT = 50


def _venue_image_subquery() -> Subquery:
    return (
        select(
            VenueImage.venue_id,
            VenueImage.image_url,
            func.row_number()
            .over(
                partition_by=VenueImage.venue_id,
                order_by=(VenueImage.is_cover.desc(), VenueImage.sort_order),
            )
            .label("img_rn"),
        )
        .subquery()
    )


def _explore_venue_select(image_subquery: Subquery):
    return select(
        Venue.id,
        Venue.name,
        Venue.address,
        Venue.capacity,
        Venue.category_id,
        VenueCategory.name.label("category"),
        Location.city.label("city"),
        Location.district.label("district"),
        Location.state.label("state"),
        image_subquery.c.image_url.label("image"),
        func.min(VenueSlot.price).label("price"),
    )


def _explore_venue_group_by(image_subquery: Subquery):
    return (
        Venue.id,
        Venue.name,
        Venue.address,
        Venue.capacity,
        Venue.category_id,
        VenueCategory.name,
        Location.city,
        Location.district,
        Location.state,
        image_subquery.c.image_url,
    )


async def list_all_venues(db: AsyncSession) -> list[Venue]:
    result = await db.execute(select(Venue).order_by(Venue.id))
    return list(result.scalars().all())


async def get_active_approved_venues(db: AsyncSession) -> list[Venue]:
    result = await db.execute(
        select(Venue).where(
            Venue.is_active.is_(True),
            Venue.status == VenueStatus.APPROVED,
        )
    )
    return list(result.scalars().all())


async def get_venue_categories(db: AsyncSession) -> list[VenueCategory]:
    result = await db.execute(
        select(VenueCategory)
        .where(VenueCategory.is_active.is_(True))
        .order_by(VenueCategory.name)
    )
    return list(result.scalars().all())


async def get_category_by_id(
    db: AsyncSession,
    category_id: int,
) -> VenueCategory | None:
    return await db.scalar(
        select(VenueCategory).where(VenueCategory.id == category_id)
    )


async def get_location_by_id(
    db: AsyncSession,
    location_id: int,
) -> Location | None:
    return await db.scalar(
        select(Location).where(Location.id == location_id)
    )


async def explore_venues(
    db: AsyncSession,
    *,
    category_id: int | None = None,
    location_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    limit: int = EXPLORE_VENUE_DEFAULT_LIMIT,
    offset: int = 0,
) -> Sequence[RowMapping]:
    image_subquery = _venue_image_subquery()
    capped_limit = min(limit, EXPLORE_VENUE_MAX_LIMIT)

    query = (
        _explore_venue_select(image_subquery)
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
        .outerjoin(
            image_subquery,
            (Venue.id == image_subquery.c.venue_id)
            & (image_subquery.c.img_rn == 1),
        )
        .where(
            Venue.is_active.is_(True),
            Venue.status == VenueStatus.APPROVED,
        )
    )

    if category_id is not None:
        query = query.where(Venue.category_id == category_id)

    if location_id is not None:
        query = query.where(Venue.location_id == location_id)

    query = query.group_by(*_explore_venue_group_by(image_subquery))

    if min_price is not None:
        query = query.having(func.min(VenueSlot.price) >= min_price)

    if max_price is not None:
        query = query.having(func.min(VenueSlot.price) <= max_price)

    result = await db.execute(
        query.order_by(Venue.id).limit(capped_limit).offset(offset)
    )
    return result.mappings().all()


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

    image_subquery = _venue_image_subquery()

    result = await db.execute(
        _explore_venue_select(image_subquery)
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
        .outerjoin(
            image_subquery,
            (Venue.id == image_subquery.c.venue_id)
            & (image_subquery.c.img_rn == 1),
        )
        .where(ranked_subquery.c.rn == 1)
        .group_by(*_explore_venue_group_by(image_subquery))
        .order_by(VenueCategory.name)
        .limit(HOMEPAGE_VENUE_LIMIT)
    )

    return result.mappings().all()


async def create_venue(
    db: AsyncSession,
    venue_data: VenueCreate,
    owner_id: int,
) -> Venue:
    venue = Venue(
        owner_id=owner_id,
        category_id=venue_data.category_id,
        location_id=venue_data.location_id,
        name=venue_data.name,
        description=venue_data.description,
        address=venue_data.address,
        capacity=venue_data.capacity,
        booking_type=venue_data.booking_type,
        amenities=venue_data.amenities,
        status=VenueStatus.APPROVED,
        contact_name=venue_data.contact_name,
        contact_phone=venue_data.contact_phone,
        contact_email=venue_data.contact_email,
    )

    venue.images = [
        VenueImage(
            public_id=image.public_id,
            image_url=image.image_url,
            is_cover=image.is_cover,
            sort_order=image.sort_order,
        )
        for image in venue_data.images
    ]

    db.add(venue)
    await db.commit()
    await db.refresh(venue)
    return venue
