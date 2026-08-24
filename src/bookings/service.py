from sqlalchemy.ext.asyncio import AsyncSession

from bookings.models import Booking, BookingStatus, BookingTableSlot
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
        status=BookingStatus.BOOKING,
    )

    session.add(booking)
    await session.flush()

    for item in booking_data.tables_slots:
        booking_table_slot = BookingTableSlot(
            booking_id=booking.id,
            table_id=item.table_id,
            slot_id=item.slot_id,
        )
        session.add(booking_table_slot)

    await session.commit()
    await session.refresh(booking)

    return booking


async def update_booking(
    session: AsyncSession,
    booking: Booking,
    booking_data: BookingUpdate,
) -> Booking:
    """Обновляет бронирование."""
    await validate_booking_is_updatable(booking)

    data = booking_data.model_dump(exclude_unset=True)

    cafe_id = data.get("cafe_id", booking.cafe_id)
    booking_date = data.get("booking_date", booking.booking_date)
    tables_slots = data.get("tables_slots")

    if tables_slots is not None:
        await validate_cafe_exists(
            session=session,
            cafe_id=cafe_id,
        )

        await validate_tables_and_slots(
            session=session,
            cafe_id=cafe_id,
            tables_slots=tables_slots,
        )

        await validate_no_overlap(
            session=session,
            booking_date=booking_date,
            tables_slots=tables_slots,
            exclude_booking_id=booking.id,
        )

    for field, value in data.items():
        if field != "tables_slots":
            setattr(booking, field, value)

    if tables_slots is not None:
        booking_table_slots = await session.scalars(
            BookingTableSlot.__table__.select().where(
                BookingTableSlot.booking_id == booking.id,
            ),
        )

        for booking_table_slot in booking_table_slots:
            await session.delete(booking_table_slot)

        for item in tables_slots:
            session.add(
                BookingTableSlot(
                    booking_id=booking.id,
                    table_id=item.table_id,
                    slot_id=item.slot_id,
                ),
            )

    await session.commit()
    await session.refresh(booking)

    return booking


async def cancel_booking(
    session: AsyncSession,
    booking: Booking,
) -> Booking:
    """Отменяет бронирование."""
    await validate_booking_is_updatable(booking)

    booking.status = BookingStatus.CANCELED

    await session.commit()
    await session.refresh(booking)

    return booking
