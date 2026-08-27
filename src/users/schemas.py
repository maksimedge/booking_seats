import re
import uuid
from datetime import datetime
from typing import Optional, Self

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from users.constants import (
    PASSWORD_MIN_LENGTH,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    UserRole,
)


class UserCreate(BaseModel):
    """Схема создания пользователя."""

    username: str = Field(
        ...,
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
    )
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Проверяет формат телефона."""
        if value is None:
            return value
        digits = re.sub(r'[^0-9]', '', value)
        if len(digits) < 7:
            raise ValueError('Телефон должен содержать не менее 7 цифр')
        return value

    @model_validator(mode='after')
    def check_email_or_phone(self) -> Self:
        """Проверяет, что указан email или телефон."""
        if not self.email and not self.phone:
            raise ValueError('Необходимо указать email или phone')
        return self


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""

    username: Optional[str] = Field(
        None,
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH,
    )
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=PASSWORD_MIN_LENGTH)
    is_active: Optional[bool] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, value: Optional[str]) -> Optional[str]:
        """Проверяет формат телефона."""
        if value is None:
            return value
        digits = re.sub(r'[^0-9]', '', value)
        if len(digits) < 7:
            raise ValueError('Телефон должен содержать не менее 7 цифр')
        return value


class UserShortInfo(BaseModel):
    """Краткая информация о пользователе."""

    id: uuid.UUID  # было int, исправлено
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
