from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from users import crud

from core.exceptions import AppException
from core.logger import logger


async def check_username_unique(
    db: AsyncSession,
    username: str | None,
    exclude_user_id: int | None = None,
) -> None:
    """Проверяет, что username не занят другим пользователем."""
    if username is None:
        return
    user = await crud.get_user_by_username(db, username)
    if user and (exclude_user_id is None or user.id != exclude_user_id):
        logger.warning('Попытка создания пользователя с уже существующим username: {}', username)
        raise AppException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Пользователь с таким username уже существует',
        )


async def check_email_unique(db: AsyncSession, email: str | None, exclude_user_id: int | None = None) -> None:
    """Проверяет, что email не занят другим пользователем."""
    if email is None:
        return
    user = await crud.get_user_by_email(db, email)
    if user is not None and (exclude_user_id is None or user.id != exclude_user_id):
        logger.warning('Попытка использования уже существующего email: {}', email)
        raise AppException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Пользователь с таким email уже существует',
        )


async def check_phone_unique(db: AsyncSession, phone: str | None, exclude_user_id: int | None = None) -> None:
    """Проверяет, что телефон не занят другим пользователем."""
    if phone is None:
        return
    user = await crud.get_user_by_phone(db, phone)
    if user is not None and (exclude_user_id is None or user.id != exclude_user_id):
        logger.warning('Попытка использования уже существующего phone: {}', phone)
        raise AppException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Пользователь с таким телефоном уже существует',
        )
