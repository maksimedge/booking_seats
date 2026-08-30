import asyncio
from uuid import UUID

from notifications.service import send_notification

from core.celery_app import booking_celery


@booking_celery.task
def send_notification_task(value: str) -> None:
    """Hello task."""
    send_notification(value)


@booking_celery.task
def periodic_test_task() -> None:
    """Beat task."""
    print('Celery Beat task выполнена')


@booking_celery.task
def booking_created_notification_task(booking_id: UUID) -> None:
    """Отправляет уведомление менеджерам кафе после создания бронирования."""
    asyncio.run(send_notification(booking_id))
    # send_notification(booking_id)
    print('Im here')
