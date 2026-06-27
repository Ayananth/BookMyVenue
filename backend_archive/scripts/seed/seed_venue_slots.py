from datetime import date, timedelta, time
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Venue, VenueSlot


async def seed_venue_slots(db: AsyncSession):
    venues = (
        await db.execute(select(Venue))
    ).scalars().all()

    slots = []

    for venue in venues:
        for i in range(7):
            slot_date = date.today() + timedelta(days=i)

            slots.extend(
                [
                    VenueSlot(
                        venue_id=venue.id,
                        slot_date=slot_date,
                        start_time=time(9, 0),
                        end_time=time(13, 0),
                        price=Decimal("10000.00"),
                    ),
                    VenueSlot(
                        venue_id=venue.id,
                        slot_date=slot_date,
                        start_time=time(14, 0),
                        end_time=time(18, 0),
                        price=Decimal("12000.00"),
                    ),
                    VenueSlot(
                        venue_id=venue.id,
                        slot_date=slot_date,
                        start_time=time(18, 0),
                        end_time=time(23, 0),
                        price=Decimal("15000.00"),
                    ),
                ]
            )

    db.add_all(slots)
    await db.commit()