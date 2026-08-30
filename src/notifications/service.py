from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bookings.models import Booking
from cafes.models import Cafe
from notifications.email import send_email

from core.db import session_maker


async def send_notification(booking_id: UUID) -> None:
    """Send notifications."""
    async with session_maker() as session:
        result = await session.execute(
            select(Booking)
            .options(selectinload(Booking.cafe).selectinload(Cafe.managers))
            .where(Booking.id == booking_id),
        )
        booking = result.scalar_one_or_none()
        for manager in booking.cafe.managers:
            send_email(booking)
