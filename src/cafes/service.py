import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.models import Cafe
from cafes.schemas import CafeCreate, CafeUpdate
from users.constants import UserRole
from users.models import User

logger = logging.getLogger(__name__)


async def create_cafe(
    db: AsyncSession,
    cafe_data: CafeCreate,
) -> Cafe:
    """Создание нового кафе."""
    result = await db.execute(
        select(Cafe).where(
            Cafe.name == cafe_data.name,
            Cafe.address == cafe_data.address,
        ),
    )
    existing: Optional[Cafe] = result.scalar_one_or_none()

    if existing:
        logger.warning(
            f'Попытка создать кафе с существующими данными: '
            f'name={cafe_data.name}, address={cafe_data.address}',
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Кафе с таким названием и адресом уже существует',
        )

    result_managers: Result = await db.execute(
        select(User).where(User.id.in_(cafe_data.managers_id)),
    )
    managers: List[User] = result_managers.scalars().all()

    if len(managers) != len(cafe_data.managers_id):
        missing = set(cafe_data.managers_id) - {m.id for m in managers}
        logger.warning(f'Менеджеры не найдены: {missing}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Один или несколько менеджеров не найдены',
        )

    for manager in managers:
        if manager.cafe_id is not None:
            logger.warning(
                f'Менеджер {manager.id} ({manager.username}) уже привязан к кафе {manager.cafe_id}',
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Менеджер {manager.username} уже привязан к другому кафе',
            )

    new_cafe: Cafe = Cafe(
        name=cafe_data.name,
        address=cafe_data.address,
        phone=cafe_data.phone,
        description=cafe_data.description,
        photo_id=cafe_data.photo_id,
    )
    db.add(new_cafe)
    await db.flush()

    for manager in managers:
        manager.cafe_id = new_cafe.id
        db.add(manager)

    await db.commit()
    await db.refresh(new_cafe)
    logger.info(f'Создано кафе: id={new_cafe.id}, name={new_cafe.name}')
    return new_cafe


async def get_cafes(
    db: AsyncSession,
    show_active: Optional[bool] = None,
    current_user: Optional[User] = None,
) -> List[Cafe]:
    """Получение списка кафе.

    Для администраторов и менеджеров — все кафе (с возможностью выбора).
    Для пользователей — только активные.
    """
    query = select(Cafe)

    if current_user is None or current_user.role == UserRole.USER:
        query = query.where(Cafe.is_active)
    elif current_user.role == UserRole.MANAGER:
        if show_active is not None:
            query = query.where(Cafe.is_active == show_active)
        else:
            query = query.where(Cafe.is_active)
    elif current_user.role == UserRole.ADMIN:
        if show_active is not None:
            query = query.where(Cafe.is_active == show_active)
    else:
        query = query.where(Cafe.is_active)

    result: Result = await db.execute(query)
    return result.scalars().all()


async def get_cafe_by_id(
    db: AsyncSession,
    cafe_id: UUID,
) -> Optional[Cafe]:
    """Получение кафе по ID."""
    query = select(Cafe).where(Cafe.id == cafe_id)
    result: Result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_cafe(
    db: AsyncSession,
    cafe: Cafe,
    update_data: CafeUpdate,
) -> Cafe:
    """Обновление данных кафе."""
    if update_data.name is not None or update_data.address is not None:
        new_name = update_data.name or cafe.name
        new_address = update_data.address or cafe.address

        result = await db.execute(
            select(Cafe).where(
                Cafe.name == new_name,
                Cafe.address == new_address,
                Cafe.id != cafe.id,
            ),
        )
        existing: Optional[Cafe] = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Кафе с таким названием и адресом уже существует',
            )

    if update_data.managers_id is not None:
        result = await db.execute(
            select(User)
            .where(User.id.in_(update_data.managers_id))
            .where(
                (User.cafe_id.is_(None)) | (User.cafe_id == cafe.id),
            ),
        )
        managers: List[User] = result.scalars().all()

        if len(managers) != len(update_data.managers_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Один или несколько менеджеров не найдены или уже привязаны',
            )

        old_managers_result = await db.execute(
            select(User).where(User.cafe_id == cafe.id),
        )
        old_managers: List[User] = old_managers_result.scalars().all()

        for old_manager in old_managers:
            old_manager.cafe_id = None
            db.add(old_manager)

        for manager in managers:
            manager.cafe_id = cafe.id
            db.add(manager)

    fields_to_update = {
        'name': update_data.name,
        'address': update_data.address,
        'phone': update_data.phone,
        'description': update_data.description,
        'photo_id': update_data.photo_id,
        'is_active': update_data.is_active,
    }
    for field, value in fields_to_update.items():
        if value is not None:
            setattr(cafe, field, value)

    await db.commit()
    await db.refresh(cafe)
    return cafe
