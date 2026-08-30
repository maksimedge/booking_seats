from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.service import get_cafe_by_id
from time_slots.models import TimeSlot
from time_slots.schemas import TimeSlotCreate, TimeSlotUpdate


async def create_time_slot(
    db: AsyncSession,
    cafe_id: UUID,
    slot_data: TimeSlotCreate,
) -> TimeSlot:
    """Создание нового временного слота для кафе."""
    cafe = await get_cafe_by_id(db, cafe_id)
    if not cafe:
        raise ValueError(f'Cafe with ID {cafe_id} not found')

    new_slot = TimeSlot(
        cafe_id=cafe_id,
        start_time=slot_data.start_time,
        end_time=slot_data.end_time,
        max_bookings=slot_data.max_bookings,
    )
    db.add(new_slot)
    await db.commit()
    await db.refresh(new_slot)
    return new_slot


async def get_time_slots_by_cafe(
    db: AsyncSession,
    cafe_id: UUID,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> List[TimeSlot]:
    """Получение списка временных слотов для конкретного кафе."""
    query = select(TimeSlot).where(TimeSlot.cafe_id == cafe_id)
    if is_active is not None:
        query = query.where(TimeSlot.is_active == is_active)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_time_slot_by_id(db: AsyncSession, slot_id: UUID) -> Optional[TimeSlot]:
    """Получение временного слота по его ID.

    Args:
        db: Сессия базы данных.
        slot_id: UUID слота.

    Returns:
        Optional[TimeSlot]: Найденный слот или None.

    """
    query = select(TimeSlot).where(TimeSlot.id == slot_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_time_slot(
    db: AsyncSession,
    slot: TimeSlot,
    update_data: TimeSlotUpdate,
) -> TimeSlot:
    """Обновление данных временного слота."""
    if update_data.start_time is not None:
        slot.start_time = update_data.start_time
    if update_data.end_time is not None:
        slot.end_time = update_data.end_time
    if update_data.max_bookings is not None:
        slot.max_bookings = update_data.max_bookings
    if update_data.is_active is not None:
        slot.is_active = update_data.is_active

    await db.commit()
    await db.refresh(slot)
    return slot
