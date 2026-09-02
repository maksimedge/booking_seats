from datetime import time
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from time_slots.constants import TIME_SLOT_MAX_BOOKINGS

from core.base_model import Base

if TYPE_CHECKING:
    from cafes.models import Cafe


class TimeSlot(Base):
    """Модель временного слота."""

    __tablename__ = 'time_slots'

    cafe_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    max_bookings: Mapped[int] = mapped_column(
        Integer,
        default=TIME_SLOT_MAX_BOOKINGS,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    cafe: Mapped['Cafe'] = relationship(
        'Cafe',
        back_populates='time_slots',
        lazy='selectin',
    )

    def __repr__(self) -> str:
        return f'<TimeSlot {self.id}: {self.start_time}-{self.end_time}>'
