from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from users.constants import (
    EMAIL_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    TG_ID_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    UserRole,
)

from core.base_model import Base

if TYPE_CHECKING:
    from cafes.models import Cafe


class User(Base):
    """Модель пользователя системы бронирования."""

    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint(
            'email IS NOT NULL OR phone IS NOT NULL',
            name='check_email_or_phone',
        ),
    )

    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH),
        unique=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(PASSWORD_HASH_MAX_LENGTH),
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String(EMAIL_MAX_LENGTH),
        unique=True,
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(PHONE_MAX_LENGTH),
        unique=True,
        nullable=True,
    )
    tg_id: Mapped[str | None] = mapped_column(
        String(TG_ID_MAX_LENGTH),
        unique=True,
        nullable=True,
    )
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name='userrole'),
        default=UserRole.USER,
        server_default=UserRole.USER.value,
        nullable=False,
    )

    cafe_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='SET NULL'),
        nullable=True,
    )

    cafe: Mapped[Optional['Cafe']] = relationship(
        'Cafe',
        back_populates='managers',
        lazy='selectin',
    )
