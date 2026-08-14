from datetime import datetime
from enum import Enum
from typing import Optional, Self

from pydantic import BaseModel, EmailStr, Field, model_validator


class UserRole(str, Enum):
    """Роли пользователей."""

    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    USER = 'USER'


class UserCreate(BaseModel):
    """Схема создания пользователя."""

    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None

    @model_validator(mode='after')
    def check_email_or_phone(self) -> Self:
        """Проверяет, что указан email или телефон."""
        if not self.email and not self.phone:
            raise ValueError('Необходимо указать email или phone')
        return self


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""

    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None


class UserShortInfo(BaseModel):
    """Краткая информация о пользователе."""

    id: int
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None

    model_config = {'from_attributes': True}


class UserInfo(UserShortInfo):
    """Полная информация о пользователе."""

    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {'from_attributes': True}


class AuthData(BaseModel):
    """Данные для входа."""

    login: str
    password: str


class AuthToken(BaseModel):
    """Токен доступа."""

    access_token: str
    token_type: str = 'bearer'
