import enum
from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cafes.models import Cafe
from tables.models import Table
from time_slots.models import TimeSlot
from users.models import User

from .constants import MAX_NOTE_LENGTH
from core.base_model import Base


class BookingTableSlot(Base):
    """Связь бронирования со столами и слотами.

    Позволяет одному бронированию иметь несколько пар (стол + слот).
    """

    __tablename__ = 'booking_tables_slots'

    booking_id: Mapped[UUID] = mapped_column(
        ForeignKey('bookings.id', ondelete='RESTRICT'),
        primary_key=True,
    )
    table_id: Mapped[UUID] = mapped_column(
        ForeignKey('tables.id', ondelete='RESTRICT'),
        primary_key=True,
    )
    slot_id: Mapped[UUID] = mapped_column(
        ForeignKey('time_slots.id', ondelete='RESTRICT'),
        primary_key=True,
    )

    booking: Mapped['Booking'] = relationship(back_populates='tables_slots')
    table: Mapped['Table'] = relationship()
    slot: Mapped['TimeSlot'] = relationship()


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

    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    cafe_id: Mapped[UUID] = mapped_column(ForeignKey('cafes.id', ondelete='RESTRICT'), nullable=False)

    booking_date: Mapped[date] = mapped_column(Date, nullable=False)
    guest_number: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(MAX_NOTE_LENGTH), nullable=True)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.BOOKING,
        nullable=False,
    )

    user: Mapped['User'] = relationship()
    cafe: Mapped['Cafe'] = relationship()
    tables_slots: Mapped[List['BookingTableSlot']] = relationship(
        back_populates='booking',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    __table_args__ = (
        CheckConstraint('guest_number >= 1', name='check_guest_number_positive'),
        CheckConstraint('booking_date >= CURRENT_DATE', name='check_booking_date_not_past'),
    )

    def __repr__(self) -> str:
        """Строковое представление объекта Booking."""
        return (
            f'Booking(id={self.id}, '
            f'user_id={self.user_id}, '
            f'cafe_id={self.cafe_id}, '
            f'booking_date={self.booking_date}, '
            f'status={self.status.value})'
        )
