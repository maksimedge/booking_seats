from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_manager_or_admin, get_current_user
from users.crud import create_user, get_all_users, get_user_by_id, update_user
from users.models import User
from users.schemas import UserCreate, UserInfo, UserUpdate

from core.db import get_session

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.post('/', response_model=UserInfo, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> UserInfo:
    """Регистрирует нового пользователя."""
    conditions = [User.username == user_create.username]
    if user_create.email is not None:
        conditions.append(User.email == user_create.email)
    if user_create.phone is not None:
        conditions.append(User.phone == user_create.phone)

    result = await db.execute(select(User).where(*conditions))
    if result.scalars().first() is not None:
        raise HTTPException(
            status_code=400,
            detail='Пользователь с такими данными уже существует',
        )
    return await create_user(db, user_create)


@router.get('/', response_model=list[UserInfo])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_session)],
    _: User = Depends(get_current_manager_or_admin),
) -> list[UserInfo]:
    """Возвращает список всех пользователей."""
    return await get_all_users(db)


@router.get('/me', response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)) -> UserInfo:
    """Возвращает информацию о текущем пользователе."""
    return current_user


@router.patch('/me', response_model=UserInfo)
async def update_me(
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_user),
) -> UserInfo:
    """Обновляет данные текущего пользователя."""
    if user_update.role is not None and user_update.role != current_user.role:
        raise HTTPException(status_code=403, detail='Нельзя изменить роль самому себе')
    if user_update.is_active is not None and user_update.is_active != current_user.is_active:
        raise HTTPException(status_code=403, detail='Нельзя изменить собственную активность')
    return await update_user(db, current_user, user_update)


@router.get('/{user_id}', response_model=UserInfo)
async def get_user(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_session)],
    _: User = Depends(get_current_manager_or_admin),
) -> UserInfo:
    """Возвращает пользователя по его ID."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return user


@router.patch('/{user_id}', response_model=UserInfo)
async def update_user_by_id(
    user_id: int,
    user_update: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_session)],
    _: User = Depends(get_current_manager_or_admin),
) -> UserInfo:
    """Обновляет данные пользователя по его ID."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return await update_user(db, user, user_update)
