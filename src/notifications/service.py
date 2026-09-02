from datetime import date, datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bookings.models import Booking, BookingStatus, BookingTableSlot
from cafes.models import Cafe
from notifications.email import send_email

from core.celery_db import celery_session_maker
from core.logger import logger

tallinn_tz = ZoneInfo('Europe/Tallinn')


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
    async with celery_session_maker() as session:
        result = await session.execute(
            select(Booking)
            .options(
                selectinload(Booking.tables_slots).selectinload(BookingTableSlot.slot),
                selectinload(Booking.user),
            )
            .where(Booking.status == BookingStatus.BOOKING)
            .where(Booking.booking_date >= date.today()),
        )
        bookings = result.scalars().all()
        test_now = datetime(
            2026,
            9,
            3,
            20,
            10,
            tzinfo=tallinn_tz,
        )

        for booking in bookings:
            earliest_slot = min(
                booking.tables_slots,
                key=lambda item: item.slot.start_time,
            )

            booking_time = datetime.combine(
                booking.booking_date,
                # time_slot.slot.start_time,
                earliest_slot.slot.start_time,
                tzinfo=tallinn_tz,
            )
            reminder_time = booking_time - timedelta(hours=1)  # add constant from settings
            reminder_sent = booking.notification_sent

            if reminder_time <= test_now < booking_time and not reminder_sent:
                print(f'I need to send reminder to {booking.user.email}')
                print(f'booking id:{booking.id}')
                print(f'booking_date:{booking.booking_date}')
                print(f'slot start:{earliest_slot.slot.start_time}')
                print(f'booking_time:{booking_time}')
                print(f'reminder_time:{reminder_time}')
                print(f'reminder_sent: {reminder_sent}')
                print(f'now:{test_now}')
                booking.notification_sent = True
                await session.commit()
