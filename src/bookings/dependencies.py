from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user
from bookings import crud
from bookings.models import Booking
from users.constants import STAFF_USER
from users.models import User

from core.db import get_session


async def get_booking_for_current_user(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> Booking:
    """Получить бронирование для текущего пользователя, проверить права."""
    booking = await crud.get_booking_with_relations(session, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Бронирование не найдено',
        )
    if booking.user_id != current_user.id and current_user.role not in STAFF_USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Нет доступа к данному бронированию',
        )
    return booking
