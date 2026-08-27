from fastapi import APIRouter

from api import auth_router, cafes_router, media_router, time_slots_router, users_router

main_router = APIRouter(prefix='/api/v1')

main_router.include_router(
    media_router,
    tags=['Media'],
)
main_router.include_router(
    auth_router,
    tags=['Users'],
)
main_router.include_router(
    users_router,
    tags=['Auth'],
)
main_router.include_router(
    cafes_router,
    tags=['Cafes'],
)
main_router.include_router(
    time_slots_router,
    tags=['Time Slots'],
)
