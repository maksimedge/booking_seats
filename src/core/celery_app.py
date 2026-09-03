from typing import Any

from celery import Celery
from celery.signals import worker_process_init

from core.logger import setup_logging
from core.settings import settings


@worker_process_init.connect
def configure_worker_logging(**kwargs: Any) -> None:
    """Настройка логирования для celery."""
    setup_logging()


booking_celery = Celery(
    'booking_notification',
    broker=settings.rabbitmq_url,
    include=['notifications.tasks'],
)


booking_celery.conf.beat_schedule = {
    'find_bookings_for_reminder_task': {
        'task': 'notifications.tasks.check_booking_reminders_task',
        'schedule': 10.0,
    },
}
