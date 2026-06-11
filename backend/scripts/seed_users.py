from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from BookMyVenue.backend.app.core.config import settings
from BookMyVenue.backend.app.core.security import hash_password
from BookMyVenue.backend.app.models import AuthAccount, AuthProvider, User, UserRole


SYNC_DATABASE_URL = settings.database_url.replace(
    "postgresql+asyncpg",
    "postgresql+psycopg",
)

engine = create_engine(SYNC_DATABASE_URL)


users = [
    {
        "name": "Admin User",
        "email": "admin@test.com",
        "password": "Admin@123",
        "role": UserRole.ADMIN,
    },
    {
        "name": "John Doe",
        "email": "john@test.com",
        "password": "Password@123",
        "role": UserRole.USER,
    },
    {
        "name": "Jane Smith",
        "email": "jane@test.com",
        "password": "Password@123",
        "role": UserRole.USER,
    },
    {
        "name": "Venue Owner",
        "email": "owner@test.com",
        "password": "Password@123",
        "role": UserRole.VENUE,
    },
]


with Session(engine) as session:
    for data in users:
        existing_user = session.scalar(
            select(User).where(User.email == data["email"])
        )
        if existing_user is not None:
            continue

        user = User(
            full_name=data["name"],
            email=data["email"],
            role=data["role"],
            is_active=True,
            is_email_verified=True,
        )

        session.add(user)
        session.flush()

        auth_account = AuthAccount(
            user_id=user.id,
            provider=AuthProvider.EMAIL,
            provider_user_id=data["email"],
            password_hash=hash_password(data["password"]),
        )

        session.add(auth_account)

    session.commit()

print("Users created successfully")
