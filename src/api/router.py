from fastapi import APIRouter

from api import media_router

main_router = APIRouter()

main_router.include_router(
    media_router,
    tags=['Media'],
)
