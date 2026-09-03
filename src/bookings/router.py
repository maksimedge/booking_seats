from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from bookings import service
from bookings.dependencies import get_booking_for_current_user
from bookings.models import Booking
from bookings.schemas import BookingCreate, BookingInfo, BookingUpdate
from users.models import User

from core.db import get_session

router = APIRouter(prefix='/booking')


@router.get(
    '',
    response_model=List[BookingInfo],
    summary='Получить список бронирований текущего пользователя',
)
async def get_my_bookings(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> List[Booking]:
    """Список бронирований текущего пользователя."""
    return await service.get_user_bookings(session, current_user.id)


@router.post(
    '',
    response_model=BookingInfo,
    status_code=status.HTTP_201_CREATED,
    summary='Создание нового бронирования',
)
async def create_booking_endpoint(
    booking_data: BookingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Booking:
    """Создание бронирования."""
    return await service.create_booking(session, booking_data, current_user.id, current_user.username)


@router.get(
    '/{booking_id}',
    response_model=BookingInfo,
    summary='Получить бронирование по ID',
)
async def get_booking(
    booking: Booking = Depends(get_booking_for_current_user),
) -> Booking:
    """Получить бронирование по ID."""
    return booking


@router.patch(
    '/{booking_id}',
    response_model=BookingInfo,
    summary='Обновление информации о бронировании по его ID',
)
async def update_booking_endpoint(
    booking_data: BookingUpdate,
    booking: Booking = Depends(get_booking_for_current_user),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Booking:
    """Эндпоинт обновления бронирования."""
    return await service.update_booking(session, booking, booking_data, current_user.username)
