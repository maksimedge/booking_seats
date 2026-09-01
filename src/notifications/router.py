from uuid import UUID

from fastapi import APIRouter

from notifications.tasks import check_booking_reminders_task

router = APIRouter(
    prefix='/notifications',
    tags=['notifications'],
)


@router.post('/test')
async def test_notification(uuid: UUID) -> dict[str, str]:
    """Test endpoint."""
    # task = booking_created_notification_task.delay(uuid)
    task = check_booking_reminders_task.delay(uuid)

    return {
        'task_id': task.id,
    }
