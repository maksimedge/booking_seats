from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from cafes.schemas import CafeShortInfo

from .constants import DESCRIPTION_MAX_LENGTH, SEAT_NUMBER_MAX, SEAT_NUMBER_MIN


class TableCreate(BaseModel):
    """Схема для создания стола."""

    seat_number: int = Field(..., description='Количество мест')
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description='Описание стола')

    @field_validator('seat_number')
    @classmethod
    def validate_seat_number(cls, value: int) -> int:
        """Проверка, что количество мест положительное."""
        if value <= 0:
            raise ValueError('Количество мест должно быть положительным числом')
        if value > SEAT_NUMBER_MAX:
            raise ValueError(f'Количество мест не может превышать {SEAT_NUMBER_MAX}')
        return value


class TableUpdate(BaseModel):
    """Схема для обновления стола."""

    seat_number: Optional[int] = Field(
        None,
        ge=SEAT_NUMBER_MIN,
        le=SEAT_NUMBER_MAX,
        description='Количество мест',
    )
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description='Описание стола')
    is_active: Optional[bool] = None

    @field_validator('seat_number')
    @classmethod
    def validate_seat_number(cls, value: Optional[int]) -> Optional[int]:
        """Проверка, что количество мест положительное."""
        if value is not None and value <= 0:
            raise ValueError('Количество мест должно быть положительным числом')
        if value is not None and value > SEAT_NUMBER_MAX:
            raise ValueError(f'Количество мест не может превышать {SEAT_NUMBER_MAX}')
        return value

    @field_validator('is_active')
    @classmethod
    def validate_is_active(cls, value: Optional[bool]) -> Optional[bool]:
        """Проверка, что is_active не null."""
        if value is None:
            raise ValueError('Поле is_active не может быть null')
        return value


class TableResponse(BaseModel):
    """Схема для ответа с данными стола."""

    id: UUID
    cafe: CafeShortInfo
    seat_number: int
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
