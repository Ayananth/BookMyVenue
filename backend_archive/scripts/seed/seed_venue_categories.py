from sqlalchemy.ext.asyncio import AsyncSession

from app.models import VenueCategory


async def seed_venue_categories(db: AsyncSession):
    categories = [
        VenueCategory(
            name="Wedding Hall",
            icon_url="https://picsum.photos/200",
        ),
        VenueCategory(
            name="Conference Hall",
            icon_url="https://picsum.photos/201",
        ),
        VenueCategory(
            name="Party Hall",
            icon_url="https://picsum.photos/202",
        ),
        VenueCategory(
            name="Auditorium",
            icon_url="https://picsum.photos/203",
        ),
    ]

    db.add_all(categories)
    await db.commit()