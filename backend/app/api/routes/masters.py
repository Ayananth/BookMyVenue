from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.repositories import master_repository
from app.schemas import DropdownItem, VenueFormDataResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.repositories import master_repository




router = APIRouter(
    prefix="/masters",
    tags=["Masters"]
)

@router.get(
    "/locations",
    response_model=list[DropdownItem]
)
async def get_locations(
    db: AsyncSession = Depends(get_db)
):
    return await master_repository.get_locations(db)


@router.get(
    "/venue-form-data",
    response_model=VenueFormDataResponse,
)
async def get_venue_form_data(
    db: AsyncSession = Depends(get_db),
):
    return await master_repository.get_venue_form_data(db)