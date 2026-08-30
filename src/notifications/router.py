from uuid import UUID

from fastapi import APIRouter

from notifications.tasks import booking_created_notification_task

router = APIRouter(
    prefix='/notifications',
    tags=['notifications'],
)


@router.post('/test')
async def test_notification(uuid: UUID) -> dict[str, str]:
    """Test endpoint."""
    task = booking_created_notification_task.delay(uuid)

    return {
        'task_id': task.id,
    }
