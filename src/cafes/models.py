from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base

# Пока закомментил связь с менеджерами, так как модуль users еще не готов

# cafe_managers = Table(
#    'cafe_managers',
#    Base.metadata,
#    Column('cafe_id', PG_UUID(as_uuid=True), ForeignKey('cafes.id', ondelete='CASCADE'), primary_key=True),
#    Column('user_id', PG_UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
# )


class Cafe(Base):
    """Модель кафе."""

    __tablename__ = 'cafes'

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    photo_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    # Связи (временно закомментированы до готовности модулей)
    # managers: Mapped[list['User']] = relationship(
    #     'User',
    #     secondary=cafe_managers,
    #     back_populates='managed_cafes',
    #     lazy='selectin'
    # )
    # tables: Mapped[list['Table']] = relationship(
    #     'Table',
    #     back_populates='cafe',
    #     lazy='selectin',
    #     cascade='all, delete-orphan'
    # )
    # time_slots: Mapped[list['TimeSlot']] = relationship(
    #     'TimeSlot',
    #     back_populates='cafe',
    #     lazy='selectin',
    #     cascade='all, delete-orphan'
    # )

    def __repr__(self) -> str:
        """Строковое представление модели."""
        return f'<Cafe {self.id}: {self.name}>'
