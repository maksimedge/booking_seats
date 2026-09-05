import logging
from datetime import time
from typing import List, Optional
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.service import get_cafe_by_id
from time_slots.models import TimeSlot
from time_slots.schemas import TimeSlotCreate, TimeSlotUpdate
from users.constants import UserRole
from users.models import User

from core.exceptions import AppException

logger = logging.getLogger(__name__)


def _parse_time(time_str: str) -> time:
    """Преобразует строку в объект time."""
    try:
        return time.fromisoformat(time_str)
    except ValueError:
        detail = f'Некорректный формат времени: {time_str}. Ожидается HH:MM:SS'
        logger.warning(detail)
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


async def _check_slot_overlap(
    db: AsyncSession,
    cafe_id: UUID,
    start: time,
    end: time,
    exclude_slot_id: Optional[UUID] = None,
) -> None:
    """Проверяет пересечение слотов."""
    query = select(TimeSlot).where(
        TimeSlot.cafe_id == cafe_id,
        TimeSlot.start_time < end,
        TimeSlot.end_time > start,
    )
    if exclude_slot_id is not None:
        query = query.where(TimeSlot.id != exclude_slot_id)

    result = await db.execute(query)
    if result.scalar_one_or_none():
        detail = 'Слот пересекается с существующим слотом'
        logger.warning(
            f'{detail}: cafe_id={cafe_id}, start={start}, end={end}',
        )
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


async def _check_duplicate_slot(
    db: AsyncSession,
    cafe_id: UUID,
    start: time,
    end: time,
    exclude_slot_id: Optional[UUID] = None,
) -> None:
    """Проверяет, что слот с таким временем уже существует."""
    query = select(TimeSlot).where(
        TimeSlot.cafe_id == cafe_id,
        TimeSlot.start_time == start,
        TimeSlot.end_time == end,
    )
    if exclude_slot_id is not None:
        query = query.where(TimeSlot.id != exclude_slot_id)

    result = await db.execute(query)
    if result.scalar_one_or_none():
        detail = 'Слот с таким временем уже существует для этого кафе'
        logger.warning(
            f'{detail}: cafe_id={cafe_id}, start={start}, end={end}',
        )
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


async def create_time_slot(
    db: AsyncSession,
    cafe_id: UUID,
    slot_data: TimeSlotCreate,
) -> TimeSlot:
    """Создание нового временного слота."""
    cafe = await get_cafe_by_id(db, cafe_id)
    if not cafe:
        detail = f'Кафе с ID {cafe_id} не найдено'
        logger.warning(detail)
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

    start = _parse_time(slot_data.start_time)
    end = _parse_time(slot_data.end_time)

    if start >= end:
        detail = 'Время начала должно быть раньше времени окончания'
        logger.warning(
            f'{detail}: cafe_id={cafe_id}, start={start}, end={end}',
        )
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    await _check_duplicate_slot(db, cafe_id, start, end)
    await _check_slot_overlap(db, cafe_id, start, end)

    new_slot = TimeSlot(
        cafe_id=cafe_id,
        start_time=start,
        end_time=end,
        description=slot_data.description,
    )
    db.add(new_slot)

    try:
        await db.commit()
        await db.refresh(new_slot)
        logger.info(
            f'Создан временной слот: id={new_slot.id}, cafe_id={cafe_id}, start={start}, end={end}',
        )
        return new_slot
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f'Ошибка при сохранении слота в БД: {e}')
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка при сохранении слота',
        )


async def get_time_slots_by_cafe(
    db: AsyncSession,
    cafe_id: UUID,
    show_active: Optional[bool] = None,
    current_user: Optional[User] = None,
) -> List[TimeSlot]:
    """Получение списка слотов для кафе с учётом роли пользователя."""
    query = select(TimeSlot).where(TimeSlot.cafe_id == cafe_id)

    if current_user is None or current_user.role == UserRole.USER:
        query = query.where(TimeSlot.is_active)
    elif current_user.role == UserRole.MANAGER:
        if show_active is not None:
            query = query.where(TimeSlot.is_active == show_active)
        else:
            query = query.where(TimeSlot.is_active)
    elif current_user.role == UserRole.ADMIN:
        if show_active is not None:
            query = query.where(TimeSlot.is_active == show_active)
    else:
        query = query.where(TimeSlot.is_active)

    result = await db.execute(query)
    slots = result.scalars().all()
    logger.info(f'Получено {len(slots)} слотов для cafe_id={cafe_id}')
    return slots


async def get_time_slot_by_id(
    db: AsyncSession,
    slot_id: UUID,
) -> Optional[TimeSlot]:
    """Получение слота по ID."""
    query = select(TimeSlot).where(TimeSlot.id == slot_id)
    result = await db.execute(query)
    slot = result.scalar_one_or_none()
    if slot:
        logger.info(f'Получен слот: id={slot_id}')
    else:
        logger.warning(f'Слот не найден: id={slot_id}')
    return slot


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
        detail = 'Время начала должно быть раньше времени окончания'
        logger.warning(
            f'{detail}: slot_id={slot.id}, start={new_start}, end={new_end}',
        )
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    if update_data.start_time is not None or update_data.end_time is not None:
        await _check_duplicate_slot(
            db,
            slot.cafe_id,
            new_start,
            new_end,
            slot.id,
        )
        await _check_slot_overlap(
            db,
            slot.cafe_id,
            new_start,
            new_end,
            slot.id,
        )

    if update_data.start_time is not None:
        slot.start_time = new_start
    if update_data.end_time is not None:
        slot.end_time = new_end
    if update_data.description is not None:
        slot.description = update_data.description
    if update_data.is_active is not None:
        slot.is_active = update_data.is_active

    try:
        await db.commit()
        await db.refresh(slot)
        logger.info(
            f'Обновлён слот: id={slot.id}, cafe_id={slot.cafe_id}, '
            f'start={slot.start_time}, end={slot.end_time}',
        )
        return slot
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f'Ошибка при обновлении слота в БД: {e}')
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка при обновлении слота',
        )
