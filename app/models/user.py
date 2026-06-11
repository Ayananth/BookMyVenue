from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    VENUE = "venue"


class AuthProvider(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    GOOGLE = "GOOGLE"


class SignupMethod(str, Enum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"


class OtpPurpose(str, Enum):
    LOGIN = "LOGIN"
    PASSWORD_RESET = "PASSWORD_RESET"
    EMAIL_CHANGE = "EMAIL_CHANGE"
    PHONE_CHANGE = "PHONE_CHANGE"


user_role_enum = SQLEnum(
    UserRole,
    name="userrole",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)

auth_provider_enum = SQLEnum(
    AuthProvider,
    name="authprovider",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)

signup_method_enum = SQLEnum(
    SignupMethod,
    name="signupmethod",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)

otp_purpose_enum = SQLEnum(
    OtpPurpose,
    name="otppurpose",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "email IS NOT NULL OR phone IS NOT NULL",
            name="must_have_contact",
        ),
        Index("idx_users_email", "email"),
        Index("idx_users_phone", "phone"),
        Index("idx_users_role", "role"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        user_role_enum,
        nullable=False,
        server_default=UserRole.USER.value,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    is_blocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    is_phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
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

    venues: Mapped[list["Venue"]] = relationship(
        back_populates="owner",
    )
    auth_accounts: Mapped[list["AuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    otp_requests: Mapped[list["OtpRequest"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class AuthAccount(Base):
    __tablename__ = "auth_accounts"

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_auth_accounts_provider_user",
        ),
        Index("idx_auth_accounts_provider", "provider"),
        Index("idx_auth_accounts_provider_user_id", "provider_user_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    provider: Mapped[AuthProvider] = mapped_column(
        auth_provider_enum,
        nullable=False,
    )
    provider_user_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    password_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="auth_accounts",
    )


class SignupRequest(Base):
    __tablename__ = "signup_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    password_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    otp_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    method: Mapped[SignupMethod] = mapped_column(
        signup_method_enum,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class OtpRequest(Base):
    __tablename__ = "otp_requests"

    __table_args__ = (
        Index("idx_otp_requests_destination", "destination"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    otp_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    purpose: Mapped[OtpPurpose] = mapped_column(
        otp_purpose_enum,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User | None"] = relationship(
        back_populates="otp_requests",
    )
