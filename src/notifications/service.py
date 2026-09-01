from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bookings.models import Booking
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
