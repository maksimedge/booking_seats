from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from bookings.constants import MAX_NOTE_LENGTH, MIN_GUEST_NUMBER
from bookings.models import BookingStatus


def validate_future_date(v: date) -> date:
    """Проверяет, что дата не в прошлом.

    Args:
        v: Дата для проверки

    Returns:
        date: Проверенная дата

    Raises:
        ValueError: Если дата в прошлом

    """
    if v < date.today():
        raise ValueError('Нельзя бронировать на прошедшую дату')
    return v


class BookingCreate(BaseModel):
    """Схема для создания нового бронирования.

    Используется при POST-запросе на /api/v1/booking.
    Все поля обязательны, кроме note.
    """

    cafe_id: int = Field(..., description='ID кафе')
    table_id: int = Field(..., description='ID стола')
    slot_id: int = Field(..., description='ID временного слота')
    booking_date: date = Field(..., description='Дата бронирования (YYYY-MM-DD)')
    guest_number: int = Field(..., ge=MIN_GUEST_NUMBER, description='Количество гостей (минимум 1)')
    note: Optional[str] = Field(None, max_length=MAX_NOTE_LENGTH, description='Заметка к бронированию')

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        """Проверяет, что дата бронирования не в прошлом."""
        return validate_future_date(v)


class BookingUpdate(BaseModel):
    """Схема для обновления бронирования.

    Используется при PATCH-запросе на /api/v1/booking/{id}.
    Все поля опциональны — обновляются только переданные.
    """

    table_id: Optional[int] = Field(None, description='ID стола')
    slot_id: Optional[int] = Field(None, description='ID временного слота')
    booking_date: Optional[date] = Field(None, description='Дата бронирования (YYYY-MM-DD)')
    guest_number: Optional[int] = Field(None, ge=MIN_GUEST_NUMBER, description='Количество гостей')
    note: Optional[str] = Field(None, max_length=MAX_NOTE_LENGTH, description='Заметка')
    status: Optional[BookingStatus] = Field(None, description='Статус бронирования')

    @field_validator('booking_date')
    @classmethod
    def validate_booking_date(cls, v: Optional[date]) -> Optional[date]:
        """Проверяет, что дата бронирования не в прошлом.

        Если дата не передана (None) — пропускаем валидацию.
        """
        if v is not None:
            return validate_future_date(v)
        return v


class BookingInfo(BaseModel):
    """Схема для получения информации о бронировании."""

    id: int = Field(..., description='ID бронирования')
    user_id: int = Field(..., description='ID пользователя')
    cafe_id: int = Field(..., description='ID кафе')
    table_id: int = Field(..., description='ID стола')
    slot_id: int = Field(..., description='ID временного слота')
    booking_date: date = Field(..., description='Дата бронирования')
    guest_number: int = Field(..., description='Количество гостей')
    note: Optional[str] = Field(None, description='Заметка')
    status: BookingStatus = Field(..., description='Статус бронирования')
    is_active: bool = Field(..., description='Активно ли бронирование')
    created_at: datetime = Field(..., description='Дата и время создания')
    updated_at: datetime = Field(..., description='Дата и время обновления')

    class Config:
        """Настройки Pydantic для работы с SQLAlchemy."""

        from_attributes = True
