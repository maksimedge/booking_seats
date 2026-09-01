from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cafes.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    CAFE_PHONE_MAX_LENGTH,
)

from core.base_model import Base

if TYPE_CHECKING:
    from time_slots.models import TimeSlot
    from users.models import User


class Cafe(Base):
    """Модель кафе."""

    __tablename__: str = 'cafes'

    name: Mapped[str] = mapped_column(
        String(CAFE_NAME_MAX_LENGTH),
        nullable=False,
        index=True,
    )
    address: Mapped[str] = mapped_column(
        String(CAFE_ADDRESS_MAX_LENGTH),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(CAFE_PHONE_MAX_LENGTH),
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_id: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('images.id', ondelete='SET NULL'),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    managers: Mapped[List['User']] = relationship(
        'User',
        back_populates='cafe',
        lazy='selectin',
    )

    time_slots: Mapped[List['TimeSlot']] = relationship(
        'TimeSlot',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<Cafe {self.id}: {self.name}>'
