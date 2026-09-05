from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user, get_current_manager_or_admin
from users.models import User

from .crud import create_table as create_table_crud
from .crud import get_table_by_id, get_tables_by_cafe
from .crud import update_table as update_table_crud
from .schemas import TableCreate, TableResponse, TableUpdate
from .validators import check_manager_cafe_access
from core.db import get_session
from core.exceptions import AppException

router = APIRouter(
    prefix='/cafes',
)


@router.get(
    '/{cafe_id}/tables',
    response_model=List[TableResponse],
    summary='Список столов в кафе',
)
async def get_tables(
    cafe_id: UUID,
    only_active: Optional[bool] = Query(
        None,
        description='Фильтр по активности:\n'
        '- `true` — только активные столы\n'
        '- `false` — только неактивные столы\n'
        '- не указывать (null) — все столы (активные и неактивные)',
    ),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> List[TableResponse]:
    """Получить список столов кафе."""
    await check_manager_cafe_access(db, cafe_id, current_user)

    if current_user.role == 'USER':
        only_active = True

    return await get_tables_by_cafe(db, cafe_id, only_active)


@router.get(
    '/{cafe_id}/tables/{table_id}',
    response_model=TableResponse,
    summary='Информация о столе в кафе по его ID',
)
async def get_table(
    cafe_id: UUID,
    table_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> TableResponse:
    """Получить информацию о столе по ID."""
    await check_manager_cafe_access(db, cafe_id, current_user)
    table = await get_table_by_id(db, table_id)

    if not table:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )

    if table.cafe_id != cafe_id:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден в кафе {cafe_id}',
        )

    if current_user.role == 'USER' and not table.is_active:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )
    return table


@router.post(
    '/{cafe_id}/tables',
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    summary='Новый стол в кафе',
)
async def create_table(
    cafe_id: UUID,
    table_data: TableCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_manager_or_admin),
) -> TableResponse:
    """Создать новый стол."""
    await check_manager_cafe_access(db, cafe_id, current_user)
    return await create_table_crud(db, cafe_id, table_data)


@router.patch(
    '/{cafe_id}/tables/{table_id}',
    response_model=TableResponse,
    summary='Обновление информации о столе в кафе по его ID',
)
async def update_table(
    cafe_id: UUID,
    table_id: UUID,
    update_data: TableUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_manager_or_admin),
) -> TableResponse:
    """Обновить данные стола. Только для админов и менеджеров."""
    await check_manager_cafe_access(db, cafe_id, current_user)

    table = await get_table_by_id(db, table_id)
    if not table:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )

    if table.cafe_id != cafe_id:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден в кафе {cafe_id}',
        )

    updated = await update_table_crud(db, table_id, update_data)
    if not updated:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )
    return updated
