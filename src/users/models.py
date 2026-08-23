from sqlalchemy import CheckConstraint, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from users.constants import (
    EMAIL_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    TG_ID_MAX_LENGTH,
    USERNAME_MAX_LENGTH,
    UserRole,
)

from core.base_model import Base


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
