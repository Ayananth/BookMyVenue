from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from BookMyVenue.backend.app.db.base import Base


class VenueStatus(str, Enum):
    APPROVED = "approved"
    PENDING_APPROVAL = "pending_approval"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


venue_status_enum = SQLEnum(
    VenueStatus,
    name="venuestatus",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)


class Location(Base):
    __tablename__ = "locations"

    __table_args__ = (
        CheckConstraint(
            "latitude IS NULL OR latitude BETWEEN -90 AND 90",
            name="ck_locations_latitude",
        ),
        CheckConstraint(
            "longitude IS NULL OR longitude BETWEEN -180 AND 180",
            name="ck_locations_longitude",
        ),
        Index("ix_locations_city", "city"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    latitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )
    longitude: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 7),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    venues: Mapped[list["Venue"]] = relationship(
        back_populates="location",
    )


class VenueCategory(Base):
    __tablename__ = "venue_categories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    icon_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )

    venues: Mapped[list["Venue"]] = relationship(
        back_populates="category",
    )


class Venue(Base):
    __tablename__ = "venues"

    __table_args__ = (
        CheckConstraint(
            "capacity > 0",
            name="ck_venues_capacity_positive",
        ),
        Index("ix_venues_owner_id", "owner_id"),
        Index("ix_venues_category_id", "category_id"),
        Index("ix_venues_location_id", "location_id"),
        Index("ix_venues_status", "status"),
        Index(
            "ix_venues_category_status",
            "category_id",
            "status",
        ),
        Index(
            "ix_venues_location_status",
            "location_id",
            "status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("venue_categories.id"),
        nullable=False,
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    address: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[VenueStatus] = mapped_column(
        venue_status_enum,
        nullable=False,
        server_default=VenueStatus.PENDING_APPROVAL.value,
    )
    amenities: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    owner: Mapped["User"] = relationship(
        back_populates="venues",
    )
    category: Mapped["VenueCategory"] = relationship(
        back_populates="venues",
    )
    location: Mapped["Location"] = relationship(
        back_populates="venues",
    )
    images: Mapped[list["VenueImage"]] = relationship(
        back_populates="venue",
        cascade="all, delete-orphan",
    )
    slots: Mapped[list["VenueSlot"]] = relationship(
        back_populates="venue",
        cascade="all, delete-orphan",
    )


class VenueImage(Base):
    __tablename__ = "venue_images"

    __table_args__ = (
        Index("ix_venue_images_venue_id", "venue_id"),
        Index(
            "ix_venue_images_venue_sort",
            "venue_id",
            "sort_order",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    venue_id: Mapped[int] = mapped_column(
        ForeignKey(
            "venues.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    image_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_cover: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    venue: Mapped["Venue"] = relationship(
        back_populates="images",
    )


class VenueSlot(Base):
    __tablename__ = "venue_slots"

    __table_args__ = (
        CheckConstraint(
            "price >= 0",
            name="ck_venue_slots_price",
        ),
        CheckConstraint(
            "end_time > start_time",
            name="ck_venue_slots_time_range",
        ),
        UniqueConstraint(
            "venue_id",
            "slot_date",
            "start_time",
            "end_time",
            name="uq_venue_slot",
        ),
        Index(
            "ix_venue_slots_venue_date",
            "venue_id",
            "slot_date",
        ),
        Index(
            "ix_venue_slots_booking_search",
            "venue_id",
            "slot_date",
            "is_available",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    venue_id: Mapped[int] = mapped_column(
        ForeignKey(
            "venues.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    slot_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    venue: Mapped["Venue"] = relationship(
        back_populates="slots",
    )
