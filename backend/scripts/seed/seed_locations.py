from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Location


async def seed_locations(db: AsyncSession):
    locations = [
        Location(
            city="Alappuzha",
            district="Alappuzha",
            state="Kerala",
            latitude=Decimal("9.4981000"),
            longitude=Decimal("76.3388000"),
        ),
        Location(
            city="Kottayam",
            district="Kottayam",
            state="Kerala",
            latitude=Decimal("9.5916000"),
            longitude=Decimal("76.5222000"),
        ),
        Location(
            city="Kochi",
            district="Ernakulam",
            state="Kerala",
            latitude=Decimal("9.9312000"),
            longitude=Decimal("76.2673000"),
        ),
        Location(
            city="Trivandrum",
            district="Thiruvananthapuram",
            state="Kerala",
            latitude=Decimal("8.5241000"),
            longitude=Decimal("76.9366000"),
        ),
    ]

    db.add_all(locations)
    await db.commit()