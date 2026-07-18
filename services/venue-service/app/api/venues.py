from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.catalog import (
    CityDropdownOut,
    DistrictCityGroupOut,
    DistrictOut,
    VenueCategoryOut,
)
from app.services.catalog import CatalogService

router = APIRouter(prefix="/venues", tags=["venues"])


@router.get("/categories", response_model=list[VenueCategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> list[VenueCategoryOut]:
    """List active venue categories."""
    return await CatalogService(db).list_categories()


@router.get("/districts", response_model=list[DistrictOut])
async def list_districts(
    db: AsyncSession = Depends(get_db),
) -> list[DistrictOut]:
    """List all districts."""
    return await CatalogService(db).list_districts()


@router.get("/cities", response_model=list[CityDropdownOut])
async def list_cities(
    district_id: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[CityDropdownOut]:
    """List cities, optionally filtered by district_id."""
    return await CatalogService(db).list_cities(district_id=district_id)


@router.get("/location-groups", response_model=list[DistrictCityGroupOut])
async def list_location_groups(
    db: AsyncSession = Depends(get_db),
) -> list[DistrictCityGroupOut]:
    """List districts with their nested cities (for location pickers)."""
    return await CatalogService(db).list_location_groups()


@router.get("/")
async def list_venues():
    return {"items": [], "message": "Venue service is ready"}
