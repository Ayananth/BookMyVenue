from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Venue, VenueImage


async def seed_venue_images(db: AsyncSession):
    venues = (
        await db.execute(select(Venue))
    ).scalars().all()

    images = []

    for venue in venues:
        images.extend(
            [
                VenueImage(
                    venue_id=venue.id,
                    image_url=f"https://picsum.photos/800/600?random={venue.id}1",
                    is_cover=True,
                    sort_order=1,
                ),
                VenueImage(
                    venue_id=venue.id,
                    image_url=f"https://picsum.photos/800/600?random={venue.id}2",
                    sort_order=2,
                ),
                VenueImage(
                    venue_id=venue.id,
                    image_url=f"https://picsum.photos/800/600?random={venue.id}3",
                    sort_order=3,
                ),
            ]
        )

    db.add_all(images)
    await db.commit()