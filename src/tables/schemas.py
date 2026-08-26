from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .constants import DESCRIPTION_MAX_LENGTH


class TableCreate(BaseModel):
    """Схема для создания стола."""

    cafe_id: UUID = Field(..., description='ID кафе, к которому относится стол')
    seats_count: int = Field(..., ge=1, description='Количество мест (минимум 1)')
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description='Описание стола')


class TableUpdate(BaseModel):
    """Схема для обновления стола."""

    cafe_id: Optional[UUID] = Field(None, description='ID кафе')
    seats_count: Optional[int] = Field(None, ge=1, description='Количество мест')
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description='Описание стола')


class TableResponse(BaseModel):
    """Схема для ответа с данными стола."""

    id: UUID
    cafe_id: UUID
    seats_count: int
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
