from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.repositories import venue_repository
from app.models import Venue, VenueStatus
from app.schemas.venue import (
    HomePageVenueCategoryResponse,
    HomepageVenueResponse,
    VenueResponse,
)

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






@router.get("/home", response_model=list[HomepageVenueResponse])
async def get_homepage_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await venue_repository.get_homepage_venues(db)


@router.get("/explore", response_model=list[HomepageVenueResponse])
async def explore_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int | None = None,
    limit: int = Query(
        default=venue_repository.EXPLORE_VENUE_DEFAULT_LIMIT,
        ge=1,
        le=venue_repository.EXPLORE_VENUE_MAX_LIMIT,
    ),
    offset: int = Query(default=0, ge=0),
):
    return await venue_repository.explore_venues(
        db,
        category_id=category_id,
        limit=limit,
        offset=offset,
    )


@router.get("/categories", response_model=list[HomePageVenueCategoryResponse])
async def get_venue_categories(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    return await venue_repository.get_venue_categories(db)
    