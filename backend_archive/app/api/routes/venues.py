from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.deps import get_current_user
from app.models import User, UserRole
from app.queries import venue_queries
from app.schemas.venue import (
    HomePageVenueCategoryResponse,
    HomepageVenueResponse,
    VenueCreate,
    VenueCreateResponse,
    VenueResponse,
)

router = APIRouter(prefix="/venues", tags=["Venues"])


@router.get("/all", response_model=list[VenueResponse])
async def list_all_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await venue_queries.list_all_venues(db)


@router.get("/", response_model=list[VenueResponse])
async def get_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await venue_queries.get_active_approved_venues(db)


@router.get("/home", response_model=list[HomepageVenueResponse])
async def get_homepage_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await venue_queries.get_homepage_venues(db)


@router.get("/explore", response_model=list[HomepageVenueResponse])
async def explore_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
    category_id: int | None = None,
    location_id: int | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    limit: int = Query(
        default=venue_queries.EXPLORE_VENUE_DEFAULT_LIMIT,
        ge=1,
        le=venue_queries.EXPLORE_VENUE_MAX_LIMIT,
    ),
    offset: int = Query(default=0, ge=0),
):
    return await venue_queries.explore_venues(
        db,
        category_id=category_id,
        location_id=location_id,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )


@router.get("/categories", response_model=list[HomePageVenueCategoryResponse])
async def get_venue_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await venue_queries.get_venue_categories(db)


@router.post("/add", response_model=VenueCreateResponse, status_code=201)
async def add_venue(
    venue: VenueCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != UserRole.VENUE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only venue owners can add venues",
        )

    category = await venue_queries.get_category_by_id(db, venue.category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    location = await venue_queries.get_location_by_id(db, venue.location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")

    cover_count = sum(1 for image in venue.images if image.is_cover)
    if cover_count > 1:
        raise HTTPException(
            status_code=400,
            detail="Only one cover image is allowed",
        )

    if venue.images and cover_count == 0:
        venue.images[0].is_cover = True

    return await venue_queries.create_venue(db, venue, current_user.id)
