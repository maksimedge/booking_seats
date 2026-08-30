from celery import Celery

from core.settings import settings

booking_celery = Celery(
    'booking_notification',
    broker=settings.rabbitmq_url,
    include=['notifications.tasks'],
)


booking_celery.conf.beat_schedule = {
    'some_periodic_task': {
        'task': 'notifications.tasks.periodic_test_task',
        'schedule': 10.0,
    },
}
