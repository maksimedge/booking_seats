from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Table
from .schemas import TableCreate, TableUpdate


async def get_table_by_id(db: AsyncSession, table_id: int) -> Table | None:
    """Получить стол по ID."""
    result = await db.execute(select(Table).where(Table.id == table_id))
    return result.scalar_one_or_none()


async def get_tables_by_cafe(
    db: AsyncSession,
    cafe_id: int,
    only_active: bool = True,
) -> list[Table]:
    """Получить все столы кафе."""
    query = select(Table).where(Table.cafe_id == cafe_id)
    if only_active:
        query = query.where(Table.is_active)
    result = await db.execute(query)
    return result.scalars().all()


async def create_table(db: AsyncSession, table_data: TableCreate) -> Table:
    """Создать новый стол."""
    new_table = Table(**table_data.model_dump())
    db.add(new_table)
    try:
        await db.commit()
        await db.refresh(new_table)
        return new_table
    except IntegrityError as e:
        await db.rollback()
        if 'foreign key' in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Cafe with id {table_data.cafe_id} not found',
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Database integrity error',
        )


async def update_table(
    db: AsyncSession,
    table_id: int,
    table_update: TableUpdate,
) -> Table | None:
    """Обновить данные стола."""
    table = await get_table_by_id(db, table_id)
    if not table:
        return None

    update_data = table_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(table, key, value)

    try:
        await db.commit()
        await db.refresh(table)
        return table
    except IntegrityError as e:
        await db.rollback()
        if 'foreign key' in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Cafe with id {table_update.cafe_id} not found',
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Database integrity error',
        )


async def delete_table(db: AsyncSession, table_id: int) -> bool:
    """Мягкое удаление (деактивация) стола."""
    table = await get_table_by_id(db, table_id)
    if not table:
        return False

    table.is_active = False
    await db.commit()
    return True
