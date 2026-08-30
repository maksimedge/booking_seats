from datetime import date
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bookings import crud
from bookings.models import Booking, BookingStatus
from bookings.schemas import BookingCreate, BookingUpdate
from bookings.validators import validate_cafe_exists, validate_no_overlap, validate_tables_and_slots
from notifications.tasks import booking_created_notification_task, booking_updated_notification_task


async def create_booking(
    session: AsyncSession,
    booking_data: BookingCreate,
    user_id: UUID,
) -> Booking:
    """Сервис создания бронирования с валидацией."""
    await validate_cafe_exists(session=session, cafe_id=booking_data.cafe_id)
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

    created_booking = await crud.create_booking_record(session, booking_data, user_id)

    # таск отправки сообщений для celery
    booking_created_notification_task.delay(created_booking.id)

    return created_booking


async def update_booking(
    session: AsyncSession,
    booking: Booking,
    booking_data: BookingUpdate,
) -> Booking:
    """Сервис обновления бронирования с проверкой даты и статуса."""
    if booking.booking_date < date.today():
        raise HTTPException(
            status_code=400,
            detail='Нельзя изменять прошедшее бронирование',
        )
    if booking.status != BookingStatus.BOOKING:
        raise HTTPException(
            status_code=400,
            detail='Изменить можно только бронирование со статусом BOOKING',
        )
    update_data = booking_data.model_dump(exclude_unset=True)
    updated_booking = await crud.update_booking_record(session, booking, update_data)
    booking_updated_notification_task.delay(updated_booking.id)
    return updated_booking


async def cancel_booking(session: AsyncSession, booking: Booking) -> Booking:
    """Сервис отмены бронирования с проверкой."""
    if booking.booking_date < date.today():
        raise HTTPException(
            status_code=400,
            detail='Нельзя отменить прошедшее бронирование',
        )
    if booking.status != BookingStatus.BOOKING:
        raise HTTPException(
            status_code=400,
            detail='Отменить можно только бронирование со статусом BOOKING',
        )
    return await crud.cancel_booking_record(session, booking)
