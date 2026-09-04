import asyncio
import smtplib
from uuid import UUID

from notifications.service import find_booking_for_notification, send_notification

from core.celery_app import booking_celery


@booking_celery.task(
    autoretry_for=(smtplib.SMTPException, OSError),
    retry_backoff=True,
    max_retries=3,
)
def booking_created_notification_task(booking_id: UUID) -> None:
    """Отправляет уведомление менеджерам кафе после создания бронирования."""
    asyncio.run(send_notification(booking_id, False))


@booking_celery.task(
    autoretry_for=(smtplib.SMTPException, OSError),
    retry_backoff=True,
    max_retries=3,
)
def booking_updated_notification_task(booking_id: UUID) -> None:
    """Отправляет уведомление менеджерам кафе после обновления бронирования."""
    asyncio.run(send_notification(booking_id, True))


@booking_celery.task
def check_booking_reminders_task() -> None:
    """Check notifications."""
    asyncio.run(find_booking_for_notification())
