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
