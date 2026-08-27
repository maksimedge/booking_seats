from celery import Celery

from core.settings import settings

booking_celery = Celery(
    'booking_notification',
    broker=settings.rabbitmq_url,
    include=['notifications.tasks'],
)
