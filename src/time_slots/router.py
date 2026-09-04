import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import (
    get_current_active_user,
    get_current_manager_or_admin,
)
from time_slots import service
from time_slots.schemas import TimeSlotCreate, TimeSlotInfo, TimeSlotUpdate
from users.models import User

from core.db import get_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/cafes/{cafe_id}/time_slots')


@router.get(
    '/',
    response_model=List[TimeSlotInfo],
    summary='Список временных слотов в кафе',
)
async def get_time_slots(
    cafe_id: UUID,
    show_active: Optional[bool] = Query(
        None,
        description=(
            'Показывать все слоты в кафе, только активные или только не активные.\n'
            'По умолчанию показывает:\n'
            '- для пользователя: только активные слоты в кафе '
            '(всегда, независимо от значения параметра).\n'
            '- для администратора: все слоты в кафе (активные и неактивные).\n'
            '- для менеджера: активные слоты в кафе.'
        ),
    ),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> List[TimeSlotInfo]:
    """Получение списка временных слотов."""
    logger.info(f'Fetching time slots for cafe_id={cafe_id}')
    return await service.get_time_slots_by_cafe(
        db,
        cafe_id,
        show_active,
        current_user,
    )


@router.post(
    '/',
    response_model=TimeSlotInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Новый временный слот в кафе',
)
async def create_time_slot(
    cafe_id: UUID,
    slot_data: TimeSlotCreate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_manager_or_admin),
) -> TimeSlotInfo:
    """Создание временного слота (только для менеджеров и админов)."""
    try:
        result = await service.create_time_slot(db, cafe_id, slot_data)
        logger.info(f'Created time slot: id={result.id}, cafe_id={cafe_id}')
        return result
    except HTTPException as e:
        logger.warning(f'Failed to create time slot: {e.detail}')
        raise


@router.get(
    '/{slot_id}',
    response_model=TimeSlotInfo,
    summary='Информация о временном слоте в кафе по его ID',
)
async def get_time_slot(
    cafe_id: UUID,
    slot_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> TimeSlotInfo:
    """Получение временного слота по ID."""
    slot = await service.get_time_slot_by_id(db, slot_id)
    if not slot or slot.cafe_id != cafe_id:
        logger.warning(
            f'Time slot not found: slot_id={slot_id}, cafe_id={cafe_id}',
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Time slot not found',
        )
    logger.info(f'Fetched time slot: id={slot_id}')
    return slot


@router.patch(
    '/{slot_id}',
    response_model=TimeSlotInfo,
    summary='Обновление информации о временном слоте в кафе по его ID',
)
async def update_time_slot(
    cafe_id: UUID,
    slot_id: UUID,
    update_data: TimeSlotUpdate,
    db: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_manager_or_admin),
) -> TimeSlotInfo:
    """Обновление временного слота (только для менеджеров и админов)."""
    slot = await service.get_time_slot_by_id(db, slot_id)
    if not slot or slot.cafe_id != cafe_id:
        logger.warning(
            f'Time slot not found for update: slot_id={slot_id}, cafe_id={cafe_id}',
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Time slot not found',
        )

    result = await service.update_time_slot(db, slot, update_data)
    logger.info(f'Updated time slot: id={slot_id}')
    return result
