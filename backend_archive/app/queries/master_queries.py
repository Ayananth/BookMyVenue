from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Location, VenueCategory
from app.models.venue import BookingType

COMMON_AMENITIES = [
    "Parking",
    "AC",
    "WiFi",
    "Projector",
    "Dining Hall",
    "Generator",
    "Stage",
    "Sound System",
]


async def get_locations(db: AsyncSession) -> list[tuple[int, str]]:
    result = await db.execute(
        select(Location.id, Location.city)
        .where(Location.is_active.is_(True))
        .order_by(Location.city)
    )
    return list(result.all())


async def get_categories(db: AsyncSession) -> list[tuple[int, str]]:
    result = await db.execute(
        select(VenueCategory.id, VenueCategory.name)
        .where(VenueCategory.is_active.is_(True))
        .order_by(VenueCategory.name)
    )
    return list(result.all())


def get_booking_types() -> list[tuple[int, str]]:
    return [
        (index, booking_type.value)
        for index, booking_type in enumerate(BookingType, start=1)
    ]


def get_amenities() -> list[tuple[int, str]]:
    return [
        (index, amenity)
        for index, amenity in enumerate(COMMON_AMENITIES, start=1)
    ]


async def get_venue_form_data(db: AsyncSession) -> dict:
    return {
        "locations": await get_locations(db),
        "categories": await get_categories(db),
        "booking_types": get_booking_types(),
        "amenities": get_amenities(),
    }
