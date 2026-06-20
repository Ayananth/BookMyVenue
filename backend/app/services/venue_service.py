from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.venue import (
    VenueCreate,
)
from app.models.user import UserRole
from app.repositories import venue_repository

class VenueService:

    async def create_venue(
        self,
        db: AsyncSession,
        venue_data: VenueCreate,
        owner: User,
    ):
        if owner.role != UserRole.VENUE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only venue owners can create venues",
            )

        return await venue_repository.create_venue(
            db=db,
            venue_data=venue_data,
            owner_id=owner.id,
        )


venue_service = VenueService()