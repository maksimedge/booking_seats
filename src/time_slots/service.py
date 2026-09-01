from datetime import time
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.service import get_cafe_by_id
from time_slots.models import TimeSlot
from time_slots.schemas import TimeSlotCreate, TimeSlotUpdate


def _parse_time(time_str: str) -> time:
    """Преобразует строку в объект time."""
    try:
        return time.fromisoformat(time_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Некорректный формат времени: {time_str}. Ожидается HH:MM:SS',
        )


async def create_time_slot(
    db: AsyncSession,
    cafe_id: UUID,
    slot_data: TimeSlotCreate,
) -> TimeSlot:
    """Создание нового временного слота."""
    cafe = await get_cafe_by_id(db, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )

    start = _parse_time(slot_data.start_time)
    end = _parse_time(slot_data.end_time)

    if start >= end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время начала должно быть раньше времени окончания',
        )

    existing = await db.execute(
        select(TimeSlot).where(
            TimeSlot.cafe_id == cafe_id,
            TimeSlot.start_time == start,
            TimeSlot.end_time == end,
        ),
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Слот с таким временем уже существует для этого кафе',
        )

    new_slot = TimeSlot(
        cafe_id=cafe_id,
        start_time=start,
        end_time=end,
        description=slot_data.description,
    )
    db.add(new_slot)
    await db.commit()
    await db.refresh(new_slot)
    return new_slot


async def get_time_slots_by_cafe(
    db: AsyncSession,
    cafe_id: UUID,
    show_active: Optional[bool] = None,
) -> List[TimeSlot]:
    """Получение списка слотов для кафе."""
    query = select(TimeSlot).where(TimeSlot.cafe_id == cafe_id)
    if show_active is not None:
        query = query.where(TimeSlot.is_active == show_active)
    result = await db.execute(query)
    return result.scalars().all()


async def get_time_slot_by_id(
    db: AsyncSession,
    slot_id: UUID,
) -> Optional[TimeSlot]:
    """Получение слота по ID."""
    query = select(TimeSlot).where(TimeSlot.id == slot_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_time_slot(
    db: AsyncSession,
    slot: TimeSlot,
    update_data: TimeSlotUpdate,
) -> TimeSlot:
    """Обновление данных временного слота."""
    new_start = slot.start_time
    new_end = slot.end_time

    if update_data.start_time is not None:
        new_start = _parse_time(update_data.start_time)

    if update_data.end_time is not None:
        new_end = _parse_time(update_data.end_time)

    if new_start >= new_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Время начала должно быть раньше времени окончания',
        )

    if update_data.start_time is not None or update_data.end_time is not None:
        existing = await db.execute(
            select(TimeSlot).where(
                TimeSlot.cafe_id == slot.cafe_id,
                TimeSlot.start_time == new_start,
                TimeSlot.end_time == new_end,
                TimeSlot.id != slot.id,
            ),
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Слот с таким временем уже существует для этого кафе',
            )

    if update_data.start_time is not None:
        slot.start_time = new_start
    if update_data.end_time is not None:
        slot.end_time = new_end
    if update_data.description is not None:
        slot.description = update_data.description
    if update_data.is_active is not None:
        slot.is_active = update_data.is_active

    await db.commit()
    await db.refresh(slot)
    return slot
