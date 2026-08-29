import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from time_slots import service
from time_slots.schemas import TimeSlotCreate, TimeSlotInfo, TimeSlotUpdate

from core.db import get_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/cafes/{cafe_id}/time_slots', tags=['Time Slots'])


@router.get('/', response_model=List[TimeSlotInfo])
async def get_time_slots(
    cafe_id: UUID,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
) -> List[TimeSlotInfo]:
    """Получение списка временных слотов для кафе."""
    logger.info(f'Fetching time slots for cafe_id={cafe_id}')
    return await service.get_time_slots_by_cafe(db, cafe_id, skip, limit, is_active)


@router.post('/', response_model=TimeSlotInfo, status_code=status.HTTP_201_CREATED)
async def create_time_slot(
    cafe_id: UUID,
    slot_data: TimeSlotCreate,
    db: AsyncSession = Depends(get_session),
) -> TimeSlotInfo:
    """Создание нового временного слота."""
    try:
        return await service.create_time_slot(db, cafe_id, slot_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get('/{slot_id}', response_model=TimeSlotInfo)
async def get_time_slot(
    cafe_id: UUID,
    slot_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> TimeSlotInfo:
    """Получение временного слота по ID."""
    slot = await service.get_time_slot_by_id(db, slot_id)
    if not slot or slot.cafe_id != cafe_id:
        logger.warning(f'Time slot not found: slot_id={slot_id}, cafe_id={cafe_id}')
        raise HTTPException(status_code=404, detail='Time slot not found')
    logger.info(f'Fetched time slot: id={slot_id}')
    return slot


@router.patch('/{slot_id}', response_model=TimeSlotInfo)
async def update_time_slot(
    cafe_id: UUID,
    slot_id: UUID,
    update_data: TimeSlotUpdate,
    db: AsyncSession = Depends(get_session),
) -> TimeSlotInfo:
    """Обновление данных временного слота."""
    slot = await service.get_time_slot_by_id(db, slot_id)
    if not slot or slot.cafe_id != cafe_id:
        logger.warning(f'Time slot not found for update: slot_id={slot_id}, cafe_id={cafe_id}')
        raise HTTPException(status_code=404, detail='Time slot not found')

    result = await service.update_time_slot(db, slot, update_data)
    logger.info(f'Updated time slot: id={slot_id}')
    return result
