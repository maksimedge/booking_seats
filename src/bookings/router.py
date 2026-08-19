from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from bookings import service
from bookings.models import Booking
from bookings.schemas import BookingCreate, BookingInfo, BookingUpdate
from core.db import get_session
from users.models import User
from auth.dependencies import get_current_user

router = APIRouter(prefix='/api/v1/booking', tags=['booking'])


@router.post('', response_model=BookingInfo, status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(
    booking_data: BookingCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Booking:
    """Создать бронирование."""
    return await service.create_booking(session, booking_data, current_user.id)


@router.patch('/{booking_id}', response_model=BookingInfo)
async def update_booking_endpoint(
    booking_id: UUID,
    booking_data: BookingUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Booking:
    """Изменить бронирование."""
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail='Бронирование не найдено')
    return await service.update_booking(session, booking, booking_data)


@router.patch('/{booking_id}/cancel', response_model=BookingInfo)
async def cancel_booking_endpoint(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Booking:
    """Отменить бронирование."""
    booking = await session.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail='Бронирование не найдено')
    return await service.cancel_booking(session, booking)
