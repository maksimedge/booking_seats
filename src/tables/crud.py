from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Table
from .schemas import TableCreate, TableUpdate
from core.logger import log_action, logger


async def get_table_by_id(db: AsyncSession, table_id: UUID) -> Table | None:
    """Получить стол по ID."""
    result = await db.execute(
        select(Table).options(selectinload(Table.cafe)).where(Table.id == table_id),
    )
    return result.scalar_one_or_none()


async def get_tables_by_cafe(
    db: AsyncSession,
    cafe_id: UUID,
    only_active: bool = True,
) -> list[Table]:
    """Получить все столы кафе."""
    query = select(Table).options(selectinload(Table.cafe)).where(Table.cafe_id == cafe_id)
    if only_active:
        query = query.where(Table.is_active)
    result = await db.execute(query)
    return result.scalars().all()


async def create_table(db: AsyncSession, cafe_id: UUID, table_data: TableCreate) -> Table:
    """Создать новый стол."""
    new_table = Table(
        cafe_id=cafe_id,
        seat_number=table_data.seat_number,
        description=table_data.description,
    )
    db.add(new_table)
    try:
        await db.commit()
        await db.refresh(new_table)
        await db.refresh(new_table, attribute_names=['cafe'])

        log_action(
            'Создана запись',
            table='tables',
            cafe_id=cafe_id,
            seat_number=table_data.seat_number,
        )
        return new_table

    except IntegrityError as e:
        await db.rollback()

        error_msg = str(e).lower()
        if 'foreign key' in error_msg:
            logger.warning(
                f'Невозможно создать стол: кафе id={cafe_id} не найдено',
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Кафе с id {cafe_id} не найдено',
            )

        logger.error(f'Ошибка при создании стола: {str(e)}')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка базы данных',
        )


async def update_table(
    db: AsyncSession,
    table_id: UUID,
    table_update: TableUpdate,
) -> Table | None:
    """Обновить данные стола."""
    table = await get_table_by_id(db, table_id)
    if not table:
        logger.warning(f'Стол id={table_id} не найден')
        return None

    old_seat_number = table.seat_number
    update_data = table_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(table, key, value)

    try:
        await db.commit()
        await db.refresh(table)
        await db.refresh(table, attribute_names=['cafe'])

        changes = []
        if 'seat_number' in update_data and old_seat_number != table.seat_number:
            changes.append(f'Изменено количество мест: {old_seat_number} -> {table.seat_number}')
        if 'description' in update_data:
            changes.append('Обновлено описание')
        if 'is_active' in update_data:
            changes.append(f'Статус активности: {"активен" if table.is_active else "неактивен"}')
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
                detail=f'Кафе с id {table_update.cafe_id} не найдено',
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Ошибка базы данных',
        )
