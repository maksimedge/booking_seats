from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookings.models import Booking, BookingStatus, BookingTableSlot
from bookings.schemas import BookingCreate, BookingUpdate
from bookings.validators import (
    validate_cafe_exists,
    validate_no_overlap,
    validate_tables_and_slots,
)


async def _get_booking_with_relations(
    session: AsyncSession,
    booking_id: int,
) -> Booking:
    """Получает бронирование со всеми связями для ответа API."""
    query = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.cafe),
            selectinload(Booking.tables_slots).selectinload(
                BookingTableSlot.table,
            ),
            selectinload(Booking.tables_slots).selectinload(
                BookingTableSlot.slot,
            ),
        )
    )

    result = await session.execute(query)
    return result.scalar_one()


async def create_booking(
    session: AsyncSession,
    booking_data: BookingCreate,
    user_id: int,
) -> Booking:
    """Создаёт новое бронирование."""
    await validate_cafe_exists(
        session=session,
        cafe_id=booking_data.cafe_id,
    )

    await validate_tables_and_slots(
        session=session,
        cafe_id=booking_data.cafe_id,
        tables_slots=booking_data.tables_slots,
    )

    await validate_no_overlap(
        session=session,
        booking_date=booking_data.booking_date,
        tables_slots=booking_data.tables_slots,
    )

    booking = Booking(
        user_id=user_id,
        cafe_id=booking_data.cafe_id,
        booking_date=booking_data.booking_date,
        guest_number=booking_data.guest_number,
        note=booking_data.note,
        status=BookingStatus.BOOKING,
    )

    session.add(booking)
    await session.flush()

    for table_slot in booking_data.tables_slots:
        session.add(
            BookingTableSlot(
                booking_id=booking.id,
                table_id=table_slot.table_id,
                slot_id=table_slot.slot_id,
            ),
        )

    await session.commit()

    return await _get_booking_with_relations(
        session,
        booking.id,
    )


async def update_booking(
    session: AsyncSession,
    booking: Booking,
    booking_data: BookingUpdate,
) -> Booking:
    """Изменяет бронирование."""
    if booking.booking_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя изменять прошедшее бронирование',
        )

    if booking.status != BookingStatus.BOOKING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Изменить можно только бронирование со статусом BOOKING',
        )

    update_data = booking_data.model_dump(exclude_unset=True)

    tables_slots = update_data.pop('tables_slots', None)

    if tables_slots is not None:
        for table_slot in booking.tables_slots:
            await session.delete(table_slot)

        for table_slot in tables_slots:
            session.add(
                BookingTableSlot(
                    booking_id=booking.id,
                    table_id=table_slot['table_id'],
                    slot_id=table_slot['slot_id'],
                ),
            )

    for field, value in update_data.items():
        setattr(booking, field, value)

    await session.commit()

    return await _get_booking_with_relations(
        session,
        booking.id,
    )


async def cancel_booking(
    session: AsyncSession,
    booking: Booking,
) -> Booking:
    """Отменяет бронирование."""
    if booking.booking_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя отменить прошедшее бронирование',
        )

    if booking.status != BookingStatus.BOOKING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Отменить можно только бронирование со статусом BOOKING',
        )

    booking.status = BookingStatus.CANCELED

    await session.commit()

    return await _get_booking_with_relations(
        session,
        booking.id,
    )
