from datetime import time
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Time
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base_model import Base

if TYPE_CHECKING:
    from cafes.models import Cafe


class TimeSlot(Base):
    """Модель временного слота."""

    __tablename__ = 'time_slots'

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    cafe_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('cafes.id', ondelete='CASCADE'),
    )
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
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
