from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.schemas import CafeCreate, CafeInfo, CafeShortInfo, CafeUpdate
from cafes.service import CafeService

from core.db import get_session

router = APIRouter(prefix='/cafes', tags=['cafes'])


@router.get(
    '/',
    response_model=List[CafeShortInfo],
    summary='Получение списка кафе',
)
async def get_cafes(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
) -> List[CafeShortInfo]:
    """Получение списка кафе с пагинацией и фильтрацией."""
    return await CafeService.get_all(db, skip=skip, limit=limit, is_active=is_active)


@router.post(
    '/',
    response_model=CafeInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Создание нового кафе',
)
async def create_cafe(
    cafe_data: CafeCreate,
    db: AsyncSession = Depends(get_session),
) -> CafeInfo:
    """Создание нового кафе."""
    return await CafeService.create(db, cafe_data)


@router.get(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Получение информации о кафе по ID',
)
async def get_cafe(
    cafe_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> CafeInfo:
    """Получение информации о кафе по его ID."""
    cafe = await CafeService.get_by_id(db, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )
    return cafe


@router.patch(
    '/{cafe_id}',
    response_model=CafeInfo,
    summary='Обновление информации о кафе',
)
async def update_cafe(
    cafe_id: UUID,
    update_data: CafeUpdate,
    db: AsyncSession = Depends(get_session),
) -> CafeInfo:
    """Обновление информации о кафе по его ID."""
    cafe = await CafeService.get_by_id(db, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )
    return await CafeService.update(db, cafe, update_data)
