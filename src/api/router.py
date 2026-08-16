from fastapi import APIRouter

from cafes.router import router as cafes_router

main_router = APIRouter()

main_router.include_router(cafes_router, prefix='/api/v1')
