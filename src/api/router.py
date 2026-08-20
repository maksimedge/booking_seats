from fastapi import APIRouter

from auth.router import router as auth_router
from cafes.router import router as cafes_router
from users.router import router as users_router

main_router = APIRouter()

main_router.include_router(auth_router, prefix='/api/v1')
main_router.include_router(users_router, prefix='/api/v1')

main_router.include_router(cafes_router, prefix='/api/v1')
