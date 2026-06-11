from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).order_by(User.id))
    return result.scalars().all()


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if user_in.email is None and user_in.phone is None:
        raise HTTPException(
            status_code=400,
            detail="Email or phone is required",
        )

    if user_in.email is not None:
        existing_user = await db.scalar(
            select(User).where(User.email == user_in.email)
        )
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Email already registered")

    if user_in.phone is not None:
        existing_user = await db.scalar(
            select(User).where(User.phone == user_in.phone)
        )
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Phone already registered")

    user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone=user_in.phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
