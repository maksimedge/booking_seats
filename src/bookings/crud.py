from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bookings.models import Booking, BookingStatus, BookingTableSlot
from bookings.schemas import BookingCreate


async def get_booking_with_relations(
    session: AsyncSession,
    booking_id: UUID,
) -> Booking | None:
    """Получить бронирование по ID с подгрузкой связанных данных."""
    query = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.cafe),
            selectinload(Booking.tables_slots).selectinload(BookingTableSlot.table),
            selectinload(Booking.tables_slots).selectinload(BookingTableSlot.slot),
        )
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_bookings_by_user(session: AsyncSession, user_id: UUID) -> list[Booking]:
    """Получить брони пользователя."""
    query = (
        select(Booking)
        .where(Booking.user_id == user_id)
        .options(
            selectinload(Booking.user),
            selectinload(Booking.cafe),
            selectinload(Booking.tables_slots).selectinload(BookingTableSlot.table),
            selectinload(Booking.tables_slots).selectinload(BookingTableSlot.slot),
        )
    )
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_booking_record(
    session: AsyncSession,
    booking_data: BookingCreate,
    user_id: UUID,
) -> Booking:
    """Создать запись бронирования в БД."""
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
        session.add(BookingTableSlot(
            booking_id=booking.id,
            table_id=table_slot.table_id,
            slot_id=table_slot.slot_id,
        ))
    await session.commit()
    return await get_booking_with_relations(session, booking.id)


async def update_booking_record(
    session: AsyncSession,
    booking: Booking,
    update_data: dict,
) -> Booking:
    """Обновить существующую запись бронирования."""
    tables_slots = update_data.pop('tables_slots', None)
    if tables_slots is not None:
        for table_slot in booking.tables_slots:
            session.delete(table_slot)
        for table_slot in tables_slots:
            session.add(BookingTableSlot(
                booking_id=booking.id,
                table_id=table_slot['table_id'],
                slot_id=table_slot['slot_id'],
            ))
    for field, value in update_data.items():
        setattr(booking, field, value)
    await session.commit()
    return await get_booking_with_relations(session, booking.id)
