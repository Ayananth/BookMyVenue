from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_user
from app.core.security import create_access_token, verify_google_token
from app.db import get_db
from app.models import AuthAccount, AuthProvider, User, UserRole
from app.schemas.user import (
    GoogleAuthRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).order_by(User.id))
    return result.scalars().all()


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


async def google_auth(
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

    auth_account = await db.scalar(
        select(AuthAccount).where(
            AuthAccount.provider == AuthProvider.GOOGLE,
            AuthAccount.provider_user_id == google_sub,
        )
    )

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
        user = await db.scalar(
            select(User).where(User.email == email)
        )

        if user:

            if user.role != expected_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"This email is associated with a "
                        f"{user.role.value} account."
                    ),
                )

            auth_account = AuthAccount(
                user_id=user.id,
                provider=AuthProvider.GOOGLE,
                provider_user_id=google_sub,
            )
            db.add(auth_account)

            if picture and not user.avatar_url:
                user.avatar_url = picture

            if name and not user.full_name:
                user.full_name = name

            user.is_email_verified = True

        else:
            user = User(
                email=email,
                full_name=name,
                avatar_url=picture,
                role=expected_role,
                is_email_verified=True,
            )

            db.add(user)
            await db.flush()

            auth_account = AuthAccount(
                user_id=user.id,
                provider=AuthProvider.GOOGLE,
                provider_user_id=google_sub,
            )

            db.add(auth_account)

    if not user.is_active or user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(
        {"sub": str(user.id)}
    )

    print(f"User {user.id} logged in with Google")
    print(access_token)
    return TokenResponse(
        access_token=access_token,
        user=user,
    )



@router.post(
    "/google",
    response_model=TokenResponse,
)
async def google_login_user(
    data: GoogleAuthRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await google_auth(
        db=db,
        token=data.token,
        expected_role=UserRole.USER,
    )


@router.post(
    "/venue/google",
    response_model=TokenResponse,
)
async def google_login_venue(
    data: GoogleAuthRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await google_auth(
        db=db,
        token=data.token,
        expected_role=UserRole.VENUE,
    )