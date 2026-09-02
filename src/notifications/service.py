from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bookings.models import Booking, BookingStatus, BookingTableSlot
from cafes.models import Cafe
from notifications.email import send_email

from core.celery_db import celery_session_maker
from core.logger import logger


async def send_notification(booking_id: UUID, updated: bool | None) -> None:
    """Send notifications."""
    async with celery_session_maker() as session:
        result = await session.execute(
            select(Booking)
            .options(selectinload(Booking.cafe).selectinload(Cafe.managers))
            .where(Booking.id == booking_id),
        )
        booking = result.scalar_one_or_none()
        for manager in booking.cafe.managers:
            if manager.email is None:
                logger.warning('У менеджера {} не указан email', manager.id)
                continue
            send_email(manager.email, booking, updated)


async def find_booking_for_notification() -> None:
    """Find booking."""
    today = date.today()
    async with celery_session_maker() as session:
        result = await session.execute(
            select(Booking)
            .options(
                selectinload(Booking.tables_slots).selectinload(BookingTableSlot.slot),
                selectinload(Booking.user),
            )
            .where(Booking.status == BookingStatus.BOOKING)
            .where(Booking.booking_date >= today),
        )
        bookings = result.scalars().all()
        reminder_sent = True
        for booking in bookings:
            for time_slot in booking.tables_slots:
                # start_time = time(time_slot.slot.start_time)
                booking_time = datetime.combine(booking.booking_date, time_slot.slot.start_time)
                # print(booking_time > datetime.now())
                print(f'booking_time: {type(booking_time)}')
                reminder_time = booking_time - timedelta(hours=1)
                print(f'booking_time: {type(reminder_time)}')
                print(booking.user.email)
                # print(f'booking_time: {type(datetime.now())}')
                if datetime.now() < reminder_time and reminder_sent:
                    print(f'I need to send reminder to {booking.user.email}')
