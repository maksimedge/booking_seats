from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
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

from core.db import get_session

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.post('/', response_model=UserInfo, status_code=HTTPStatus.CREATED)
async def register_user(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User | None = Depends(get_optional_current_user),
) -> UserInfo:
    """Регистрирует нового пользователя. Неавторизованные, администраторы и менеджеры."""
    if current_user is not None and current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Обычный пользователь не может создавать новых пользователей',
        )
    conditions = [User.username == user_create.username]
    if user_create.email is not None:
        conditions.append(User.email == user_create.email)
    if user_create.phone is not None:
        conditions.append(User.phone == user_create.phone)

    result = await db.execute(select(User).where(*conditions))
    if result.scalars().first() is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Пользователь с такими данными уже существует',
        )
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
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Нельзя изменить роль самому себе',
        )
    if user_update.is_active is not None and user_update.is_active != current_user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Нельзя изменить собственную активность',
        )
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
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не найден',
        )
    if current_user.role == UserRole.USER and user.id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только к своей записи',
        )
    return await update_user(db, user, user_update)
