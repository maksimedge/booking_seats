from fastapi import APIRouter

from api import (
    auth_router,
    booking_router,
    cafes_router,
    media_router,
    table_router,
    time_slots_router,
    users_router,
)

# temp
from notifications.router import router as notifications_router

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    media_router,
    tags=['Медиа'],
)
main_router.include_router(
    auth_router,
    tags=['Пользователи'],
)
main_router.include_router(
    users_router,
    tags=['Аутентификация'],
)
main_router.include_router(
    cafes_router,
    tags=['Кафе'],
)
main_router.include_router(
    time_slots_router,
    tags=['Временные слоты'],
)

main_router.include_router(
    booking_router,
    tags=['Бронирования'],
)

main_router.include_router(
    table_router,
    tags=['Столы'],
)

main_router.include_router(notifications_router)
