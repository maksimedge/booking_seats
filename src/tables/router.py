from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_active_user, get_current_manager_or_admin
from users.models import User

from .crud import create_table as create_table_crud
from .crud import get_table_by_id, get_tables_by_cafe
from .crud import update_table as update_table_crud
from .schemas import TableCreate, TableResponse, TableUpdate
from .validators import check_manager_cafe_access
from core.db import get_session

router = APIRouter(
    prefix='/cafes',
)


@router.get(
    '/{cafe_id}/tables',
    response_model=List[TableResponse],
)
async def get_tables(
    cafe_id: int,
    only_active: Optional[bool] = Query(True, description='Только активные'),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> List[TableResponse]:
    """Получить список столов кафе."""
    await check_manager_cafe_access(db, cafe_id, current_user)

    if current_user.role == 'USER':
        only_active = True

    if only_active is None:
        only_active = False

    return await get_tables_by_cafe(db, cafe_id, only_active)


@router.get(
    '/{cafe_id}/tables/{table_id}',
    response_model=TableResponse,
)
async def get_table(
    cafe_id: int,
    table_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
) -> TableResponse:
    """Получить информацию о столе по ID."""
    await check_manager_cafe_access(db, cafe_id, current_user)
    table = await get_table_by_id(db, table_id)

    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )

    if table.cafe_id != cafe_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден в кафе {cafe_id}',
        )

    if current_user.role == 'USER' and not table.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )
    return table


@router.post(
    '/{cafe_id}/tables',
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_table(
    cafe_id: int,
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
)
async def update_table(
    cafe_id: int,
    table_id: int,
    update_data: TableUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_manager_or_admin),
) -> TableResponse:
    """Обновить данные стола. Только для админов и менеджеров."""
    await check_manager_cafe_access(db, cafe_id, current_user)

    table = await get_table_by_id(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )

    if table.cafe_id != cafe_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден в кафе {cafe_id}',
        )

    updated = await update_table_crud(db, table_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Стол с ID {table_id} не найден',
        )
    return updated
