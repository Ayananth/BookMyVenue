from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

auth_engine = create_async_engine(settings.AUTH_DATABASE_URL, echo=False)
AuthSessionLocal = async_sessionmaker(auth_engine, expire_on_commit=False)


class AuthBase(DeclarativeBase):
    pass


async def get_auth_db() -> AsyncGenerator[AsyncSession, None]:
    async with AuthSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
