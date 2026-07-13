from sqlalchemy import (
    UUID,
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base



class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    rating_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ratings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(String(150))

    review: Mapped[str] = mapped_column(Text, nullable=False)

    is_edited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_hidden: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

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

    rating = relationship("Rating", backref="review", uselist=False)