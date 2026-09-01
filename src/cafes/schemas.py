from datetime import datetime
from typing import List, Optional, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from cafes.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_ADDRESS_MIN_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    CAFE_NAME_MIN_LENGTH,
    CAFE_PHONE_MAX_LENGTH,
)
from users.schemas import UserShortInfo


class CafeBase(BaseModel):
    """Базовая схема кафе."""

    name: str = Field(
        ...,
        min_length=CAFE_NAME_MIN_LENGTH,
        max_length=CAFE_NAME_MAX_LENGTH,
    )
    address: str = Field(
        ...,
        min_length=CAFE_ADDRESS_MIN_LENGTH,
        max_length=CAFE_ADDRESS_MAX_LENGTH,
    )
    phone: str = Field(..., max_length=CAFE_PHONE_MAX_LENGTH)
    description: Optional[str] = None
    photo_id: Optional[UUID] = None


class CafeCreate(CafeBase):
    """Схема создания кафе."""

    managers_id: List[UUID] = Field(
        ...,
        min_length=1,
        description='ID менеджеров кафе (минимум один)',
    )

    @model_validator(mode='after')
    def validate_managers(self) -> Self:
        """Проверяет, что передан хотя бы один менеджер."""
        if not self.managers_id:
            raise ValueError('Кафе должно иметь хотя бы одного менеджера')
        return self


class CafeUpdate(BaseModel):
    """Схема обновления кафе."""

    name: Optional[str] = Field(
        None,
        min_length=CAFE_NAME_MIN_LENGTH,
        max_length=CAFE_NAME_MAX_LENGTH,
    )
    address: Optional[str] = Field(
        None,
        min_length=CAFE_ADDRESS_MIN_LENGTH,
        max_length=CAFE_ADDRESS_MAX_LENGTH,
    )
    phone: Optional[str] = Field(None, max_length=CAFE_PHONE_MAX_LENGTH)
    description: Optional[str] = None
    photo_id: Optional[UUID] = None
    managers_id: Optional[List[UUID]] = Field(None, min_length=1)
    is_active: Optional[bool] = None

    @model_validator(mode='after')
    def validate_managers(self) -> Self:
        """Проверяет, что список менеджеров не пустой, если он передан."""
        if self.managers_id is not None and len(self.managers_id) == 0:
            raise ValueError('Список менеджеров не может быть пустым')
        return self


class CafeShortInfo(BaseModel):
    """Краткая информация о кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address: str
    phone: str
    description: Optional[str]
    photo_id: Optional[UUID]


class CafeInfo(CafeShortInfo):
    """Полная информация о кафе."""

    managers: List[UserShortInfo] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
