from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bookings.constants import MAX_NOTE_LENGTH, MIN_GUEST_NUMBER
from bookings.models import BookingStatus
from cafes.schemas import CafeShortInfo
from tables.schemas import TableResponse
from time_slots.schemas import TimeSlotInfo
from users.schemas import UserShortInfo


class TableSlot(BaseModel):
    """Пара (стол + слот) для бронирования."""

    table_id: int = Field(..., description='ID стола')
    slot_id: int = Field(..., description='ID временного слота')


class TableSlotInfo(BaseModel):
    """Пара (стол + слот) с полной информацией."""

    table: TableResponse = Field(..., description='Информация о столе')
    slot: TimeSlotInfo = Field(..., description='Информация о слоте')


def validate_future_date(v: date) -> date:
    """Проверяет, что дата не в прошлом."""
    if v < date.today():
        raise ValueError('Нельзя бронировать на прошедшую дату')
    return v


def validate_tables_slots_list(v: List[TableSlot]) -> List[TableSlot]:
    """Проверяет, что список пар (стол + слот) не пустой."""
    if not v:
        raise ValueError('Должен быть указан хотя бы один стол')
    return v


class BookingCreate(BaseModel):
    """Схема для создания нового бронирования."""

    cafe_id: int = Field(..., description='ID кафе')
    booking_date: date = Field(..., description='Дата бронирования (YYYY-MM-DD)')
    guest_number: int = Field(
        ...,
        ge=MIN_GUEST_NUMBER,
        description=f'Количество гостей (минимум {MIN_GUEST_NUMBER})',
    )
    note: Optional[str] = Field(
        None,
        max_length=MAX_NOTE_LENGTH,
        description=f'Заметка к бронированию (максимум {MAX_NOTE_LENGTH} символов)',
    )
    tables_slots: List[TableSlot] = Field(..., min_length=1, description='Список пар (стол + слот)')

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        """Проверяет, что дата бронирования не в прошлом."""
        return validate_future_date(v)

    @field_validator('tables_slots')
    @classmethod
    def validate_tables_slots(cls, v: Optional[List[TableSlot]]) -> Optional[List[TableSlot]]:
        """Проверяет, что список пар (стол + слот) не пустой (если передан)."""
        if v is not None and not v:
            raise ValueError('Список столов не может быть пустым')
        return v


class BookingUpdate(BaseModel):
    """Схема для обновления бронирования."""

    booking_date: Optional[date] = Field(None, description='Дата бронирования (YYYY-MM-DD)')
    guest_number: Optional[int] = Field(
        None,
        ge=MIN_GUEST_NUMBER,
        description=f'Количество гостей (минимум {MIN_GUEST_NUMBER})',
    )
    note: Optional[str] = Field(
        None,
        max_length=MAX_NOTE_LENGTH,
        description=f'Заметка (максимум {MAX_NOTE_LENGTH} символов)',
    )
    status: Optional[BookingStatus] = Field(None, description='Статус бронирования')
    tables_slots: Optional[List[TableSlot]] = Field(
        None,
        min_length=1,
        description='Список пар (стол + слот)',
    )

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: Optional[date]) -> Optional[date]:
        """Проверяет, что дата бронирования не в прошлом (если она передана)."""
        if v is not None:
            return validate_future_date(v)
        return v

    @field_validator('tables_slots')
    @classmethod
    def validate_tables_slots(cls, v: Optional[List[TableSlot]]) -> Optional[List[TableSlot]]:
        """Проверяет, что список пар (стол + слот) не пустой."""
        return validate_tables_slots_list(v)


class BookingInfo(BaseModel):
    """Схема для получения информации о бронировании."""

    id: int = Field(..., description='ID бронирования')
    user: UserShortInfo = Field(..., description='Пользователь')
    cafe: CafeShortInfo = Field(..., description='Кафе')
    booking_date: date = Field(..., description='Дата бронирования')
    guest_number: int = Field(..., description='Количество гостей')
    note: Optional[str] = Field(None, description='Заметка')
    status: BookingStatus = Field(..., description='Статус бронирования')
    is_active: bool = Field(..., description='Активно ли бронирование')
    created_at: datetime = Field(..., description='Дата и время создания')
    updated_at: datetime = Field(..., description='Дата и время обновления')
    tables_slots: List[TableSlotInfo] = Field(
        ...,
        description='Список пар (стол + слот) с полной информацией',
    )

    model_config = ConfigDict(from_attributes=True)
