from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    get_current_active_user,
    get_current_manager_or_admin,
)
from cafes import service
from cafes.schemas import CafeCreate, CafeInfo, CafeUpdate
from users.models import User

from core.db import get_session

router = APIRouter(prefix='/cafes')


@router.get(
    '/',
    response_model=List[CafeInfo],
    summary='Получение списка кафе',
)
async def get_cafes(
    show_active: Optional[bool] = Query(
        None,
        description=(
            'Показывать все кафе, только активные или только не активные.\n'
            'По умолчанию показывает:\n'
            '- для пользователя: только активные кафе '
            '(всегда, независимо от значения параметра).\n'
            '- для администратора: все кафе (активные и неактивные).\n'
            '- для менеджера: активные кафе.'
        ),
    ),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> List[CafeInfo]:
    """Получение списка кафе с учётом роли пользователя."""
    return await service.get_cafes(db, show_active, current_user)


@router.post(
    '/',
    response_model=CafeInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Создание нового кафе',
)
async def create_cafe(
    cafe_data: CafeCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_manager_or_admin),
) -> CafeInfo:
    """Создание нового кафе (только для менеджеров и админов)."""
    return await service.create_cafe(db, cafe_data)


@router.get(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Получение иформации о кафе по его ID',
)
async def get_cafe(
    cafe_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> CafeInfo:
    """Получение кафе по ID."""
    cafe = await service.get_cafe_by_id(db, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )
    return cafe


@router.patch(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Обновление иформации о кафе по его ID',
)
async def update_cafe(
    cafe_id: UUID,
    update_data: CafeUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_manager_or_admin),
) -> CafeInfo:
    """Обновление кафе (только для менеджеров и админов)."""
    cafe = await service.get_cafe_by_id(db, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )
    return await service.update_cafe(db, cafe, update_data)
