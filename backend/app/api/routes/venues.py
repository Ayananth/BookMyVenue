from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from app.services.cloudinary_service import upload_image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import RowMapping

from collections.abc import Sequence

from decimal import Decimal

from app.models import User
from app.deps import get_current_user
from app.schemas.venue import ImageUploadResponse, VenueResponse
from app.schemas.venue import (
    HomePageVenueCategoryResponse,
    HomepageVenueResponse,
    VenueCreate,
    VenueCreateResponse
)
from app.models import Venue, VenueStatus
from app.models.user import UserRole
from fastapi import HTTPException, status 



from app.db import get_db
from app.repositories import venue_repository
from app.models import Venue, VenueStatus
from app.schemas.venue import (
    HomePageVenueCategoryResponse,
    HomepageVenueResponse,
    VenueResponse,
    VenueCreate,
    VenueCreateResponse
)

router = APIRouter(
    prefix="/venues",
    tags=["Venues"],
)


@router.get("/all", response_model=list[VenueResponse])
async def list_all_venues(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Venue).order_by(Venue.id))
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
    location_id: int | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
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
        location_id=location_id,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        offset=offset,
    )


@router.get("/categories", response_model=list[HomePageVenueCategoryResponse])
async def get_venue_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    return await venue_repository.get_venue_categories(db)





@router.post("/add", response_model=VenueCreateResponse, status_code=201)
async def add_venue(
    venue: VenueCreate,
    db: Annotated[AsyncSession, Depends(get_db)], 
    current_user: Annotated[User, Depends(get_current_user)]
                    ):
    
    if current_user.role != UserRole.VENUE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only venue owners can add venues")
    
    return await venue_repository.create_venue(
        db,
        venue,
        current_user.id,
    )
    




# @router.post(
#     "/image",
#     response_model=ImageUploadResponse,
# )
# async def upload_venue_image(
#     file: UploadFile = File(...),
# ):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(
#             status_code=400,
#             detail="Only image files are allowed",
#         )

#     result = await upload_image(file)

#     return ImageUploadResponse(
#         public_id=result["public_id"],
#         url=result["url"],
#         secure_url=result["secure_url"],
#         width=result["width"],
#         height=result["height"],
#         format=result["format"],
#         bytes=result["bytes"],
#     )