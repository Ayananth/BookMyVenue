from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    venue_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    booking_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "venue_id",
            "user_id",
            name="uq_rating_user_venue",
        ),
    )