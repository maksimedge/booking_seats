from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.models import Cafe
from cafes.schemas import CafeCreate, CafeUpdate


class CafeService:
    """Сервис для работы с кафе."""

    @staticmethod
    async def create(db: AsyncSession, cafe_data: CafeCreate) -> Cafe:
        """Создание нового кафе."""
        new_cafe = Cafe(
            name=cafe_data.name,
            address=cafe_data.address,
            phone=cafe_data.phone,
            description=cafe_data.description,
            photo_id=cafe_data.photo_id,
        )
        db.add(new_cafe)
        await db.flush()

        # Добавить менеджеров, когда будет готов модуль users
        if cafe_data.managers_id:
            pass

        await db.commit()
        await db.refresh(new_cafe)
        return new_cafe

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> List[Cafe]:
        """Получение списка кафе с пагинацией и фильтрацией."""
        query = select(Cafe)
        if is_active is not None:
            query = query.where(Cafe.is_active == is_active)
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, cafe_id: UUID) -> Optional[Cafe]:
        """Получение кафе по ID."""
        query = select(Cafe).where(Cafe.id == cafe_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, cafe: Cafe, update_data: CafeUpdate) -> Cafe:
        """Обновление кафе."""
        if update_data.name is not None:
            cafe.name = update_data.name
        if update_data.address is not None:
            cafe.address = update_data.address
        if update_data.phone is not None:
            cafe.phone = update_data.phone
        if update_data.description is not None:
            cafe.description = update_data.description
        if update_data.photo_id is not None:
            cafe.photo_id = update_data.photo_id
        if update_data.is_active is not None:
            cafe.is_active = update_data.is_active

        # Обновить менеджеров когда будет готов модуль users
        if update_data.managers_id is not None:
            pass

        await db.commit()
        await db.refresh(cafe)
        return cafe
