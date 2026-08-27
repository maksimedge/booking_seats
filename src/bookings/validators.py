from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tables.models import Table

from bookings.models import Booking, BookingStatus, BookingTableSlot
from bookings.schemas import TableSlot
from cafes.models import Cafe
from time_slots.models import TimeSlot


async def validate_cafe_exists(session: AsyncSession, cafe_id: int) -> None:
    """Проверяет, что кафе существует и активно."""
    cafe = await session.get(Cafe, cafe_id)
    if not cafe or not getattr(cafe, 'is_active', True):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail='Кафе не найдено или недоступно')


async def validate_tables_and_slots(
    session: AsyncSession,
    cafe_id: int,
    tables_slots: List[TableSlot],
) -> None:
    """Проверяет, что все столы и слоты существуют, активны и принадлежат кафе."""
    for item in tables_slots:
        table = await session.get(Table, item.table_id)
        if not table or table.cafe_id != cafe_id or not getattr(table, 'is_active', True):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Стол {item.table_id} недоступен в выбранном кафе',
            )

        slot = await session.get(TimeSlot, item.slot_id)
        if not slot or slot.cafe_id != cafe_id or not getattr(slot, 'is_active', True):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail=f'Слот {item.slot_id} недоступен в выбранном кафе',
            )


async def validate_no_overlap(
    session: AsyncSession,
    booking_date: date,
    tables_slots: List[TableSlot],
    exclude_booking_id: Optional[int] = None,
) -> None:
    """Проверяет, что на указанную дату и слоты нет других активных броней на эти же столы."""
    for item in tables_slots:
        query = (
            select(BookingTableSlot)
            .join(Booking, BookingTableSlot.booking_id == Booking.id)
            .where(
                Booking.booking_date == booking_date,
                Booking.status != BookingStatus.CANCELED,
                BookingTableSlot.table_id == item.table_id,
                BookingTableSlot.slot_id == item.slot_id,
            )
        )
        if exclude_booking_id is not None:
            query = query.where(Booking.id != exclude_booking_id)
        result = await session.execute(query)
        if result.scalars().first() is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=(f'Стол {item.table_id} уже забронирован на слот {item.slot_id} в выбранную дату'),
            )


async def validate_booking_is_updatable(booking: Booking) -> None:
    """Проверяет, что бронь можно изменять/отменять."""
    if booking.booking_date < date.today():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='Нельзя изменять/отменять прошедшее бронирование',
        )
    if booking.status != BookingStatus.BOOKING:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='Изменить можно только бронирование со статусом BOOKING',
        )
