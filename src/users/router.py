from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    get_current_active_user,
    get_current_manager_or_admin,
    get_optional_current_user,
)
from users.constants import UserRole
from users.crud import create_user, get_all_users, get_user_by_id, update_user
from users.models import User
from users.schemas import UserCreate, UserInfo, UserUpdate
from users.validators import check_email_unique, check_phone_unique, check_username_unique

from core.db import get_session
from core.logger import logger

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.post('/', response_model=UserInfo, status_code=HTTPStatus.CREATED)
async def register_user(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User | None = Depends(get_optional_current_user),
) -> UserInfo:
    """Регистрирует нового пользователя. Неавторизованные, администраторы и менеджеры."""
    if current_user is not None and current_user.role == UserRole.USER:
        logger.warning('Попытка создания пользователя обычным пользователем')
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Обычный пользователь не может создавать новых пользователей',
        )

    await check_username_unique(db, user_create.username)
    await check_email_unique(db, user_create.email)
    await check_phone_unique(db, user_create.phone)

    return await create_user(db, user_create)


@router.get('/', response_model=list[UserInfo])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_session)],
    _: User = Depends(get_current_manager_or_admin),
) -> list[UserInfo]:
    """Возвращает список всех пользователей. Только для администраторов/менеджеров."""
    return await get_all_users(db)


@router.get('/me', response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_active_user)) -> UserInfo:
    """Возвращает информацию о текущем пользователе."""
    return current_user


@router.patch('/me', response_model=UserInfo)
async def update_me(
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_active_user),
) -> UserInfo:
    """Обновляет данные текущего пользователя."""
    if user_update.role is not None and user_update.role != current_user.role:
        logger.warning('Попытка изменения роли самому себе')
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Нельзя изменить роль самому себе',
        )
    if user_update.is_active is not None and user_update.is_active != current_user.is_active:
        logger.warning('Попытка изменения собственной активности')
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Нельзя изменить собственную активность',
        )

    await check_username_unique(db, user_update.username, exclude_user_id=current_user.id)
    await check_email_unique(db, user_update.email, exclude_user_id=current_user.id)
    await check_phone_unique(db, user_update.phone, exclude_user_id=current_user.id)

    return await update_user(db, current_user, user_update)


@router.get('/{user_id}', response_model=UserInfo)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_active_user),
) -> UserInfo:
    """Возвращает пользователя по ID. Обычный пользователь видит только себя."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не найден',
        )
    if current_user.role == UserRole.USER and user.id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только к своей записи',
        )
    return user


@router.patch('/{user_id}', response_model=UserInfo)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_active_user),
) -> UserInfo:
    """Обновляет пользователя по ID. Обычный пользователь обновляет только себя."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        logger.warning('Попытка изменения несуществующего пользователя, id={}', user_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не найден',
        )
    if current_user.role == UserRole.USER and user.id != current_user.id:
        logger.warning('Отказано в изменении пользователя id={}: недостаточно прав', user_id)
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только к своей записи',
        )
    # логирование блокировки/разблокировки
    if user_update.is_active is not None and user_update.is_active != user.is_active:
        if user_update.is_active:
            logger.info('Пользователь id={} разблокирован', user_id)
        else:
            logger.info('Пользователь id={} заблокирован', user_id)
    # логирование изменения роли
    if user_update.role is not None and user_update.role != user.role:
        logger.info(
            'Изменена роль пользователя id={}: {} -> {}',
            user_id,
            user.role.value,
            user_update.role.value,
        )

    await check_username_unique(db, user_update.username, exclude_user_id=user_id)
    await check_email_unique(db, user_update.email, exclude_user_id=user_id)
    await check_phone_unique(db, user_update.phone, exclude_user_id=user_id)

    return await update_user(db, user, user_update)
