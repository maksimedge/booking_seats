from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from bookings.models import Booking, BookingStatus
from bookings.schemas import BookingCreate, BookingUpdate


async def create_booking(
    session: AsyncSession,
    booking_data: BookingCreate,
    user_id: int,
) -> Booking:
    """Создаёт новое бронирование."""
    booking = Booking(
        user_id=user_id,
        **booking_data.model_dump(),
        status=BookingStatus.BOOKING,
    )
    session.add(booking)
    await session.commit()
    await session.refresh(booking)
    return booking


async def update_booking(
    session: AsyncSession,
    booking: Booking,
    booking_data: BookingUpdate,
) -> Booking:
    """Обновляет бронирование (только разрешённые поля)."""
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

    for field, value in booking_data.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)

    await session.commit()
    await session.refresh(booking)
    return booking


async def cancel_booking(session: AsyncSession, booking: Booking) -> Booking:
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
    await session.refresh(booking)
    return booking
