from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from cafes.schemas import CafeShortInfo


class TimeSlotBase(BaseModel):
    """Базовая схема временного слота."""

    start_time: time
    end_time: time
    description: Optional[str] = None


class TimeSlotCreate(TimeSlotBase):
    """Схема создания временного слота."""

    pass


class TimeSlotUpdate(BaseModel):
    """Схема обновления временного слота."""

    start_time: Optional[str] = Field(
        None,
        pattern=r'^([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)$',
        description='Время начала в формате HH:MM:SS',
    )
    end_time: Optional[str] = Field(
        None,
        pattern=r'^([0-1]\d|2[0-3]):([0-5]\d):([0-5]\d)$',
        description='Время окончания в формате HH:MM:SS',
    )
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TimeSlotInfo(TimeSlotBase):
    """Схема ответа с информацией о временном слоте."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cafe: CafeShortInfo
    start_time: time
    end_time: time
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
