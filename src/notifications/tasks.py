from core.celery_app import booking_celery


@booking_celery.task
def hello_task(value: int) -> None:
    """Hello task."""
    print(f'Получено значение: {value}')
