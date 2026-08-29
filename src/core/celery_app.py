from celery import Celery

from core.settings import settings

booking_celery = Celery(
    'booking_notification',
    broker=settings.rabbitmq_url,
    include=['notifications.tasks'],
)


booking_celery.conf.beat_schedule = {
    'some_periodic_task': {
        'task': 'some_package.tasks.some_task',
        'schedule': 60.0,
    },
}
