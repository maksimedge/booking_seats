from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    get_current_active_user,
    get_current_manager_or_admin,
    get_optional_current_user,
)
from users.crud import get_all_users
from users.models import User
from users.schemas import UserCreate, UserInfo, UserUpdate
from users.services import (
    get_user_service,
    register_user_service,
    update_me_service,
    update_user_by_id_service,
)

from core.db import get_session

router = APIRouter(prefix='/users')


@router.post('/', response_model=UserInfo, status_code=HTTPStatus.CREATED)
async def register_user(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User | None = Depends(get_optional_current_user),
) -> UserInfo:
    """Регистрирует нового пользователя. Неавторизованные, администраторы и менеджеры."""
    return await register_user_service(user_create, db, current_user)


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
    return await update_me_service(user_update, db, current_user)


@router.get('/{user_id}', response_model=UserInfo)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_active_user),
) -> UserInfo:
    """Возвращает пользователя по ID. Обычный пользователь видит только себя."""
    return await get_user_service(user_id, db, current_user)


@router.patch('/{user_id}', response_model=UserInfo)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_active_user),
) -> UserInfo:
    """Обновляет пользователя по ID. Обычный пользователь обновляет только себя."""
    return await update_user_by_id_service(user_id, user_update, db, current_user)
