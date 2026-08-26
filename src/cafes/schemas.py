from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from cafes.constants import (
    CAFE_ADDRESS_MAX_LENGTH,
    CAFE_ADDRESS_MIN_LENGTH,
    CAFE_NAME_MAX_LENGTH,
    CAFE_NAME_MIN_LENGTH,
    CAFE_PHONE_MAX_LENGTH,
)


class CafeBase(BaseModel):
    """Базовая схема для кафе."""

    name: str = Field(
        ...,
        min_length=CAFE_NAME_MIN_LENGTH,
        max_length=CAFE_NAME_MAX_LENGTH,
        description='Название кафе',
    )
    address: str = Field(
        ...,
        min_length=CAFE_ADDRESS_MIN_LENGTH,
        max_length=CAFE_ADDRESS_MAX_LENGTH,
        description='Адрес кафе',
    )
    phone: Optional[str] = Field(
        None,
        max_length=CAFE_PHONE_MAX_LENGTH,
        description='Телефон кафе',
    )
    description: Optional[str] = Field(
        None,
        description='Описание кафе',
    )
    photo_id: Optional[UUID] = Field(
        None,
        description='ID фото',
    )


class CafeCreate(CafeBase):
    """Схема для создания кафе."""

    managers_id: Optional[List[int]] = Field(
        default=[],
        description='ID менеджеров кафе',
    )


class CafeUpdate(BaseModel):
    """Схема для обновления кафе."""

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
    phone: Optional[str] = Field(
        None,
        max_length=CAFE_PHONE_MAX_LENGTH,
    )
    description: Optional[str] = None
    photo_id: Optional[UUID] = None
    managers_id: Optional[List[int]] = None
    is_active: Optional[bool] = None


class CafeShortInfo(BaseModel):
    """Краткая информация о кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address: str
    phone: Optional[str]
    description: Optional[str]
    photo_id: Optional[UUID]
    is_active: bool


class ManagerInfo(BaseModel):
    """Информация о менеджере кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class CafeInfo(CafeShortInfo):
    """Полная информация о кафе."""

    managers: List[ManagerInfo] = []
    created_at: datetime
    updated_at: datetime
