from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.models import Cafe
from users.models import User


async def check_manager_cafe_access(
    db: AsyncSession,
    cafe_id: UUID,
    current_user: User,
) -> Cafe:
    """Проверяет, что менеджер имеет доступ к кафе.

    Возвращает объект кафе, если проверка пройдена.
    """
    cafe = await db.get(Cafe, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )

    if current_user.role in ('ADMIN', 'USER'):
        return cafe

    if current_user.role == 'MANAGER':
        if current_user.id not in [m.id for m in cafe.managers]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Менеджер не управляет этим кафе',
            )
        return cafe

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Недостаточно прав',
    )
