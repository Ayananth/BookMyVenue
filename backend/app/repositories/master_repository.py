from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import Location
from app.models.venue_category import VenueCategory
from app.models.booking_type import BookingType
from app.models.amenity import Amenity



async def get_locations(db: AsyncSession):
    result = await db.execute(
        select(Location.id, Location.name)
        .order_by(Location.name)
    )
    return result.all()


async def get_categories(db: AsyncSession):
    result = await db.execute(
        select(VenueCategory.id, VenueCategory.name)
        .order_by(VenueCategory.name)
    )
    return result.all()


async def get_booking_types(db: AsyncSession):
    result = await db.execute(
        select(BookingType.id, BookingType.name)
        .order_by(BookingType.name)
    )
    return result.all()


async def get_amenities(db: AsyncSession):
    result = await db.execute(
        select(Amenity.id, Amenity.name)
        .order_by(Amenity.name)
    )
    return result.all()