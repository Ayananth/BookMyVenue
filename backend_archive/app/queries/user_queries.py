from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuthAccount, AuthProvider, User


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email))


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    return await db.scalar(select(User).where(User.phone == phone))


async def create_user(
    db: AsyncSession,
    *,
    full_name: str | None,
    email: str | None,
    phone: str | None,
) -> User:
    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_google_auth_account(
    db: AsyncSession,
    google_sub: str,
) -> AuthAccount | None:
    return await db.scalar(
        select(AuthAccount).where(
            AuthAccount.provider == AuthProvider.GOOGLE,
            AuthAccount.provider_user_id == google_sub,
        )
    )


async def link_google_account(
    db: AsyncSession,
    *,
    user: User,
    google_sub: str,
    name: str | None,
    picture: str | None,
) -> User:
    db.add(
        AuthAccount(
            user_id=user.id,
            provider=AuthProvider.GOOGLE,
            provider_user_id=google_sub,
        )
    )

    if picture and not user.avatar_url:
        user.avatar_url = picture

    if name and not user.full_name:
        user.full_name = name

    user.is_email_verified = True

    await db.commit()
    await db.refresh(user)
    return user


async def create_user_with_google_account(
    db: AsyncSession,
    *,
    email: str,
    name: str | None,
    picture: str | None,
    role,
    google_sub: str,
) -> User:
    user = User(
        email=email,
        full_name=name,
        avatar_url=picture,
        role=role,
        is_email_verified=True,
    )
    db.add(user)
    await db.flush()

    db.add(
        AuthAccount(
            user_id=user.id,
            provider=AuthProvider.GOOGLE,
            provider_user_id=google_sub,
        )
    )

    await db.commit()
    await db.refresh(user)
    return user
