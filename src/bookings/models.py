import enum
from datetime import date
from typing import Optional

from cafes.models import Cafe
from slots.models import TimeSlot
from sqlalchemy import Date, Enum, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from tables.models import Table

from users.models import User

from core.db import Base


class BookingStatus(str, enum.Enum):
    """Перечисление возможных статусов бронирования.

    Attributes:
        BOOKING: Бронирование создано, ожидает подтверждения
        CANCELED: Бронирование отменено пользователем или менеджером
        ACTIVE: Клиент пришел в кафе, бронирование активно
        COMPLETED: Обслуживание завершено, бронирование закрыто

    """

    BOOKING = 'BOOKING'
    CANCELED = 'CANCELED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'


class Booking(Base):
    """Модель бронирования стола в кафе.

    Отвечает за хранение информации о бронировании: кто, где, когда,
    на сколько человек, статус и дополнительные заметки.
    """

    __tablename__ = 'bookings'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    cafe_id: Mapped[int] = mapped_column(ForeignKey('cafes.id', ondelete='CASCADE'), nullable=False)
    table_id: Mapped[int] = mapped_column(ForeignKey('tables.id', ondelete='CASCADE'), nullable=False)
    slot_id: Mapped[int] = mapped_column(ForeignKey('time_slots.id', ondelete='CASCADE'), nullable=False)

    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    guest_number: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.BOOKING,
        nullable=False,
    )

    user: Mapped['User'] = relationship()
    cafe: Mapped['Cafe'] = relationship()
    table: Mapped['Table'] = relationship()
    slot: Mapped['TimeSlot'] = relationship()

    def __repr__(self) -> str:
        """Строковое представление объекта Booking."""
        return (
            f'Booking(id={self.id}, '
            f'user_id={self.user_id}, '
            f'cafe_id={self.cafe_id}, '
            f'table_id={self.table_id}, '
            f'slot_id={self.slot_id}, '
            f'booking_date={self.booking_date}, '
            f'status={self.status.value})'
        )
