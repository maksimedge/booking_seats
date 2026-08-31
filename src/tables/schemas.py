from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from cafes.schemas import CafeShortInfo

from .constants import DESCRIPTION_MAX_LENGTH


class TableCreate(BaseModel):
    """Схема для создания стола."""

    seat_number: int = Field(..., ge=1, description='Количество мест')
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description='Описание стола')


class TableUpdate(BaseModel):
    """Схема для обновления стола."""

    seat_number: Optional[int] = Field(None, ge=1, description='Количество мест')
    description: Optional[str] = Field(None, max_length=DESCRIPTION_MAX_LENGTH, description='Описание стола')
    is_active: Optional[bool] = None


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
