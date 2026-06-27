from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.queries import master_queries
from app.schemas.master import DropdownItem, VenueFormDataResponse

router = APIRouter(prefix="/masters", tags=["Masters"])


@router.get("/locations", response_model=list[DropdownItem])
async def get_locations(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    rows = await master_queries.get_locations(db)
    return [DropdownItem(id=row[0], name=row[1]) for row in rows]


@router.get("/venue-form-data", response_model=VenueFormDataResponse)
async def get_venue_form_data(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    data = await master_queries.get_venue_form_data(db)
    return VenueFormDataResponse(
        locations=[DropdownItem(id=row[0], name=row[1]) for row in data["locations"]],
        categories=[DropdownItem(id=row[0], name=row[1]) for row in data["categories"]],
        booking_types=[
            DropdownItem(id=row[0], name=row[1]) for row in data["booking_types"]
        ],
        amenities=[DropdownItem(id=row[0], name=row[1]) for row in data["amenities"]],
    )
