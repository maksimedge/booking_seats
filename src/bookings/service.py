from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from bookings import crud
from bookings.models import Booking
from bookings.schemas import BookingCreate, BookingUpdate, TableSlot
from bookings.validators import (
    validate_booking_is_updatable,
    validate_cafe_exists,
    validate_no_overlap,
    validate_tables_and_slots,
    validate_tables_capacity,
)

from core.logger import log_action, logger


async def create_booking(
    session: AsyncSession,
    booking_data: BookingCreate,
    user_id: UUID,
    username: str,
) -> Booking:
    """Сервис создания бронирования с валидацией."""
    await validate_cafe_exists(session=session, cafe_id=booking_data.cafe_id)
    await validate_tables_and_slots(
        session=session,
        cafe_id=booking_data.cafe_id,
        tables_slots=booking_data.tables_slots,
    )
    await validate_tables_capacity(
        session=session,
        tables_slots=booking_data.tables_slots,
        guest_number=booking_data.guest_number,
    )
    await validate_no_overlap(
        session=session,
        booking_date=booking_data.booking_date,
        tables_slots=booking_data.tables_slots,
    )
    booking = await crud.create_booking_record(session, booking_data, user_id)

    logger.info(
        f'Пользователь {username} (id={user_id}) создал бронирование '
        f'id={booking.id} в кафе {booking.cafe_id} на {booking.booking_date} '
        f'на {booking.guest_number} гостей',
    )
    log_action(
        'Создано бронирование',
        table='bookings',
        booking_id=booking.id,
        user_id=user_id,
        cafe_id=booking.cafe_id,
        guest_number=booking.guest_number,
        booking_date=booking.booking_date,
    )

    return booking


async def update_booking(
    session: AsyncSession,
    booking: Booking,
    booking_data: BookingUpdate,
    username: str,
) -> Booking:
    """Сервис обновления бронирования с проверкой даты и статуса."""
    await validate_booking_is_updatable(booking)
    update_data = booking_data.model_dump(exclude_unset=True)
    if 'tables_slots' in update_data or 'guest_number' in update_data:
        tables_slots = update_data.get('tables_slots')
        guest_number = update_data.get('guest_number')

        if tables_slots is None:
            tables_slots = [
                TableSlot(table_id=ts.table_id, slot_id=ts.slot_id) for ts in booking.tables_slots
            ]
        if guest_number is None:
            guest_number = booking.guest_number

        await validate_tables_capacity(
            session=session,
            tables_slots=tables_slots,
            guest_number=guest_number,
        )
    updated_booking = await crud.update_booking_record(session, booking, update_data)

    logger.info(
        f'Пользователь {username} (id={booking.user_id}) обновил бронирование '
        f'id={booking.id}: изменены поля {list(update_data.keys())}',
    )
    log_action(
        'Обновлено бронирование',
        table='bookings',
        booking_id=booking.id,
        user_id=booking.user_id,
        updated_fields=list(update_data.keys()),
    )
    return updated_booking


async def get_user_bookings(
    session: AsyncSession,
    user_id: UUID,
) -> list[Booking]:
    """Бронирования пользователя."""
    return await crud.get_bookings_by_user(session, user_id)
