from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from decimal import Decimal

from app.db import get_db
from app.deps import get_current_user
from app.models import User, UserRole
from app.queries import user_queries
from app.schemas.user import (
    GoogleAuthRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.core.security import create_access_token, verify_google_token

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await user_queries.list_users(db)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


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
        existing_user = await user_queries.get_user_by_email(db, user_in.email)
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Email already registered")

    if user_in.phone is not None:
        existing_user = await user_queries.get_user_by_phone(db, user_in.phone)
        if existing_user is not None:
            raise HTTPException(status_code=400, detail="Phone already registered")

    return await user_queries.create_user(
        db,
        full_name=user_in.full_name,
        email=user_in.email,
        phone=user_in.phone,
    )


async def _google_auth(
    db: AsyncSession,
    token: str,
    expected_role: UserRole,
) -> TokenResponse:
    user_info = verify_google_token(token)

    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token",
        )

    google_sub = user_info["sub"]
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account must have an email",
        )

    auth_account = await user_queries.get_google_auth_account(db, google_sub)

    if auth_account:
        user = await db.get(User, auth_account.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid account",
            )

        if user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"This email is associated with a "
                    f"{user.role.value} account."
                ),
            )
    else:
        user = await user_queries.get_user_by_email(db, email)

        if user:
            if user.role != expected_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"This email is associated with a "
                        f"{user.role.value} account."
                    ),
                )

            user = await user_queries.link_google_account(
                db,
                user=user,
                google_sub=google_sub,
                name=name,
                picture=picture,
            )
        else:
            user = await user_queries.create_user_with_google_account(
                db,
                email=email,
                name=name,
                picture=picture,
                role=expected_role,
                google_sub=google_sub,
            )

    if not user.is_active or user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    access_token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=user,
    )


@router.post("/google", response_model=TokenResponse)
async def google_login_user(
    data: GoogleAuthRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await _google_auth(
        db=db,
        token=data.token,
        expected_role=UserRole.USER,
    )


@router.post("/venue/google", response_model=TokenResponse)
async def google_login_venue(
    data: GoogleAuthRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await _google_auth(
        db=db,
        token=data.token,
        expected_role=UserRole.VENUE,
    )
