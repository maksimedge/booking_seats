from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from bookings import crud
from bookings.models import Booking
from bookings.schemas import BookingCreate, BookingUpdate
from bookings.validators import (
    validate_booking_is_updatable,
    validate_cafe_exists,
    validate_no_overlap,
    validate_tables_and_slots,
)


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
    return await crud.create_booking_record(session, booking_data, user_id)


async def update_booking(
    session: AsyncSession,
    booking: Booking,
    booking_data: BookingUpdate,
) -> Booking:
    """Сервис обновления бронирования с проверкой даты и статуса."""
    await validate_booking_is_updatable(booking)
    update_data = booking_data.model_dump(exclude_unset=True)
    return await crud.update_booking_record(session, booking, update_data)


async def get_user_bookings(
    session: AsyncSession,
    user_id: UUID,
) -> list[Booking]:
    """Бронирования пользователя."""
    return await crud.get_bookings_by_user(session, user_id)
