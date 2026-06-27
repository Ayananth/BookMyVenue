import asyncio

from app.db.session import AsyncSessionLocal

from scripts.seed.seed_locations import seed_locations
from scripts.seed.seed_venue_categories import seed_venue_categories
from scripts.seed.seed_venues import seed_venues
from scripts.seed.seed_venue_images import seed_venue_images
from scripts.seed.seed_venue_slots import seed_venue_slots


async def main():
    async with AsyncSessionLocal() as db:

        await seed_locations(db)

        await seed_venue_categories(db)

        await seed_venues(db)

        await seed_venue_images(db)

        await seed_venue_slots(db)


if __name__ == "__main__":
    asyncio.run(main())