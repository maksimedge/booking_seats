from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, ForeignKey, String, Table, Text
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

cafe_managers = Table(
    'cafe_managers',
    Base.metadata,
    Column('cafe_id', PG_UUID(as_uuid=True), ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
    Column(
        'user_id',
        PG_UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    ),
)


class Cafe(Base):
    """Модель кафе."""

    __tablename__ = 'cafes'

    name: Mapped[str] = mapped_column(String(CAFE_NAME_MAX_LENGTH), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(CAFE_ADDRESS_MAX_LENGTH), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(CAFE_PHONE_MAX_LENGTH), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    managers: Mapped[list['User']] = relationship(
        'User',
        secondary=cafe_managers,
        lazy='selectin',
    )

    time_slots: Mapped[list['TimeSlot']] = relationship(
        'TimeSlot',
        back_populates='cafe',
        lazy='selectin',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:
        return f'<Cafe {self.id}: {self.name}>'
