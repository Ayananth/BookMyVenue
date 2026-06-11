from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from BookMyVenue.backend.app.db import get_db
from BookMyVenue.backend.app.models import Venue, VenueStatus
from BookMyVenue.backend.app.schemas.venue import VenueResponse

router = APIRouter(
    prefix="/venues",
    tags=["Venues"],
)


@router.get("/all", response_model=list[VenueResponse])
async def list_all_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Venue).order_by(Venue.id)
    )
    return result.scalars().all()


@router.get("/", response_model=list[VenueResponse])
async def get_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Venue).where(
            Venue.is_active.is_(True),
            Venue.status == VenueStatus.APPROVED,
        )
    )
    return result.scalars().all()
