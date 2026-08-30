from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TimeSlotBase(BaseModel):
    """Базовая модель временного слота."""

    cafe_id: UUID
    start_time: time
    end_time: time
    max_bookings: int = Field(default=1, ge=1)


class TimeSlotCreate(BaseModel):
    """Модель для создания временного слота."""

    start_time: time
    end_time: time
    max_bookings: int = Field(default=1, ge=1)


class TimeSlotUpdate(BaseModel):
    """Модель для обновления временного слота."""

    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_bookings: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class TimeSlotInfo(TimeSlotBase):
    """Модель для отображения информации о временном слоте."""

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
