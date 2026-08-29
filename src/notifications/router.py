from fastapi import APIRouter

from notifications.tasks import send_notification_task

router = APIRouter(
    prefix='/notifications',
    tags=['notifications'],
)


@router.post('/test')
async def test_notification(message: str) -> dict[str, str]:
    """Test endpoint."""
    task = send_notification_task.delay(message)

    return {
        'task_id': task.id,
    }
