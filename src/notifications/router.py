from fastapi import APIRouter

from notifications.tasks import test_booking_reminders_task

router = APIRouter(
    prefix='/notifications',
    tags=['notifications'],
)


@router.post('/test')
async def test_notification() -> None:
    """Test endpoint."""
    # task = booking_created_notification_task.delay(uuid)
    test_booking_reminders_task.delay()

    # return {
    #     'task_id': task.id,
    # }
