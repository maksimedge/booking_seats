from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bookings.models import Booking, BookingStatus, BookingTableSlot
from bookings.schemas import TableSlot
from cafes.models import Cafe
from tables.models import Table
from time_slots.models import TimeSlot

from core.exceptions import AppException


async def validate_cafe_exists(session: AsyncSession, cafe_id: UUID) -> None:
    """Проверяет, что кафе существует и активно."""
    cafe = await session.get(Cafe, cafe_id)
    if not cafe or not getattr(cafe, 'is_active', True):
        raise AppException(status.HTTP_404_NOT_FOUND, detail='Кафе не найдено или недоступно')


async def validate_tables_and_slots(
    session: AsyncSession,
    cafe_id: UUID,
    tables_slots: List[TableSlot],
) -> None:
    """Проверяет, что все столы и слоты существуют, активны и принадлежат кафе."""
    for table_slot in tables_slots:
        table = await session.get(Table, table_slot.table_id)
        if not table or table.cafe_id != cafe_id or not getattr(table, 'is_active', True):
            raise AppException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Стол {table_slot.table_id} недоступен в выбранном кафе',
            )

        slot = await session.get(TimeSlot, table_slot.slot_id)
        if not slot or slot.cafe_id != cafe_id or not getattr(slot, 'is_active', True):
            raise AppException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Слот {table_slot.slot_id} недоступен в выбранном кафе',
            )


async def validate_no_overlap(
    session: AsyncSession,
    booking_date: date,
    tables_slots: List[TableSlot],
    exclude_booking_id: Optional[UUID] = None,
) -> None:
    """Проверяет, что на указанную дату и слоты нет других активных броней на эти же столы."""
    for table_slot in tables_slots:
        query = (
            select(BookingTableSlot)
            .join(Booking, BookingTableSlot.booking_id == Booking.id)
            .where(
                Booking.booking_date == booking_date,
                Booking.status != BookingStatus.CANCELED,
                BookingTableSlot.table_id == table_slot.table_id,
                BookingTableSlot.slot_id == table_slot.slot_id,
            )
        )
        if exclude_booking_id is not None:
            query = query.where(Booking.id != exclude_booking_id)
        result = await session.execute(query)
        if result.scalars().first() is not None:
            raise AppException(
                status.HTTP_409_CONFLICT,
                detail=(
                    f'Стол {table_slot.table_id} уже забронирован '
                    f'на слот {table_slot.slot_id} в выбранную дату'
                ),
            )


async def validate_booking_is_updatable(booking: Booking) -> None:
    """Проверяет, что бронь можно изменять/отменять."""
    if booking.booking_date < date.today():
        raise AppException(
            status.HTTP_400_BAD_REQUEST,
            detail='Нельзя изменять/отменять прошедшее бронирование',
        )
    if booking.status != BookingStatus.BOOKING:
        raise AppException(
            status.HTTP_400_BAD_REQUEST,
            detail='Изменить можно только бронирование со статусом BOOKING',
        )


async def validate_tables_capacity(
    session: AsyncSession,
    tables_slots: List[TableSlot],
    guest_number: int,
) -> None:
    """Проверяет, что количество гостей не превышает суммарную вместимость выбранных столов."""
    total_capacity = 0
    for table_slot in tables_slots:
        table = await session.get(Table, table_slot.table_id)
        if table:
            total_capacity += table.seat_number
        else:
            raise AppException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Стол {table_slot.table_id} не найден',
            )

    if total_capacity == 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Не выбран ни один стол',
        )

    if guest_number > total_capacity:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f'Количество гостей ({guest_number}) превышает '
                f'суммарную вместимость выбранных столов ({total_capacity})'
            ),
        )
