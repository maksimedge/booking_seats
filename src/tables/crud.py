from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Table
from .schemas import TableCreate, TableUpdate
from core.logger import log_action, logger


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
        log_action(
            'Создана запись',
            table='tables',
            cafe_id=table_data.cafe_id,
            seats_count=table_data.seats_count,
        )
        return new_table

    except IntegrityError as e:
        await db.rollback()

        error_msg = str(e).lower()
        if 'foreign key' in error_msg:
            logger.warning(
                f'Невозможно создать стол: кафе id={table_data.cafe_id} не найдено',
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Cafe with id {table_data.cafe_id} not found',
            )

        logger.error(f'Ошибка при создании стола: {str(e)}')
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
        logger.warning(f'Стол id={table_id} не найден')
        return None

    old_seats_count = table.seats_count
    old_cafe_id = table.cafe_id

    update_data = table_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(table, key, value)

    try:
        await db.commit()
        await db.refresh(table)
        changes = []
        if 'seats_count' in update_data and old_seats_count != table.seats_count:
            changes.append(f'Изменено количество мест: {old_seats_count} -> {table.seats_count}')
        if 'cafe_id' in update_data and old_cafe_id != table.cafe_id:
            changes.append(f'Изменен кафе: {old_cafe_id} -> {table.cafe_id}')
        if 'description' in update_data:
            changes.append('Обновлено описание')

        if changes:
            for change in changes:
                log_action(
                    change,
                    table='tables',
                    table_id=table_id,
                )
        else:
            log_action(
                'Обновлена запись',
                table='tables',
                table_id=table_id,
            )

        return table
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e).lower()

        logger.error(
            f'Ошибка при обновлении записи в таблице tables, id={table_id}: {str(e)}',
        )

        if 'foreign key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Cafe with id {table_update.cafe_id} not found',
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Database integrity error',
        )
