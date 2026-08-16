from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CafeBase(BaseModel):
    """Базовые поля для кафе."""

    name: str = Field(..., min_length=1, max_length=255, description='Название кафе')
    address: str = Field(..., min_length=1, max_length=255, description='Адрес кафе')
    phone: Optional[str] = Field(None, max_length=20, description='Телефон кафе')
    description: Optional[str] = Field(None, description='Описание кафе')
    photo_id: Optional[UUID] = Field(None, description='ID фото')


class CafeCreate(CafeBase):
    """Схема для создания нового кафе."""

    managers_id: Optional[List[UUID]] = Field(
        default=[],
        description='Список ID менеджеров кафе',
    )


class CafeUpdate(BaseModel):
    """Схема для обновления данных кафе."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description='Название кафе')
    address: Optional[str] = Field(None, min_length=1, max_length=255, description='Адрес кафе')
    phone: Optional[str] = Field(None, max_length=20, description='Телефон кафе')
    description: Optional[str] = Field(None, description='Описание кафе')
    photo_id: Optional[UUID] = Field(None, description='ID фото')
    managers_id: Optional[List[UUID]] = Field(None, description='Список ID менеджеров кафе')
    is_active: Optional[bool] = Field(None, description='Активно ли кафе')


class CafeShortInfo(BaseModel):
    """Краткая информация о кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description='ID кафе')
    name: str = Field(..., description='Название кафе')
    address: str = Field(..., description='Адрес кафе')
    phone: Optional[str] = Field(None, description='Телефон кафе')
    description: Optional[str] = Field(None, description='Описание кафе')
    photo_id: Optional[UUID] = Field(None, description='ID фото')
    is_active: bool = Field(..., description='Активно ли кафе')


class ManagerInfo(BaseModel):
    """Информация о менеджере кафе."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description='ID менеджера')
    username: str = Field(..., description='Имя пользователя')
    email: str = Field(..., description='Email менеджера')


class CafeInfo(CafeShortInfo):
    """Полная информация о кафе."""

    managers: List[ManagerInfo] = Field(default=[], description='Список менеджеров кафе')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')
