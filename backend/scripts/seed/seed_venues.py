from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Location,
    User,
    Venue,
    VenueCategory,
    VenueStatus,
)


async def seed_venues(db: AsyncSession):
    owner = (
        await db.execute(
            select(User)
            .where(User.role == "venue")
            .limit(1)
        )
    ).scalar_one()

    if owner is None:
        owner = 1

    locations = (
        await db.execute(
            select(Location)
        )
    ).scalars().all()

    categories = (
        await db.execute(
            select(VenueCategory)
        )
    ).scalars().all()

    venues = [
        Venue(
            owner_id=owner.id,
            category_id=categories[0].id,
            location_id=locations[0].id,
            name="Grand Wedding Palace",
            description="Premium wedding venue.",
            address="Near KSRTC Stand",
            capacity=1000,
            status=VenueStatus.APPROVED,
            amenities=[
                "Parking",
                "AC",
                "Dining Hall",
                "Generator",
            ],
        ),
        Venue(
            owner_id=owner.id,
            category_id=categories[1].id,
            location_id=locations[1].id,
            name="Tech Convention Center",
            description="Ideal for conferences.",
            address="MC Road",
            capacity=500,
            status=VenueStatus.APPROVED,
            amenities=[
                "Projector",
                "WiFi",
                "AC",
            ],
        ),
    ]

    db.add_all(venues)
    await db.commit()