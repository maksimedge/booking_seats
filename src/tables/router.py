# src/tables/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from .crud import create_table as create_table_crud
from .crud import delete_table as delete_table_crud
from .crud import get_table_by_id, get_tables_by_cafe
from .crud import update_table as update_table_crud
from .schemas import TableCreate, TableResponse, TableUpdate
from core.db import get_session

router = APIRouter(
    prefix='/cafe/tables',
    tags=['Tables'],
)


@router.get('/', response_model=List[TableResponse])
async def get_tables(
    cafe_id: int = Query(..., description='ID кафе'),
    only_active: bool = Query(True, description='Только активные'),
    db: AsyncSession = Depends(get_session),
) -> List[TableResponse]:
    """Получить список столов кафе."""
    return await get_tables_by_cafe(db, cafe_id, only_active)


@router.get('/{table_id}', response_model=TableResponse)
async def get_table(
    table_id: int,
    db: AsyncSession = Depends(get_session),
) -> TableResponse:
    """Получить информацию о столе."""
    table = await get_table_by_id(db, table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Table with id {table_id} not found',
        )
    return table


@router.post('/', response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
    table_data: TableCreate,
    db: AsyncSession = Depends(get_session),
) -> TableResponse:
    """Создать новый стол."""
    return await create_table_crud(db, table_data)


@router.patch('/{table_id}', response_model=TableResponse)
async def update_table(
    table_id: int,
    table_update: TableUpdate,
    db: AsyncSession = Depends(get_session),
) -> TableResponse:
    """Обновить данные стола."""
    updated_table = await update_table_crud(db, table_id, table_update)
    if not updated_table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Table with id {table_id} not found',
        )
    return updated_table


@router.delete('/{table_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
    table_id: int,
    db: AsyncSession = Depends(get_session),
) -> None:
    """Деактивировать стол."""
    deleted = await delete_table_crud(db, table_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Table with id {table_id} not found',
        )
    return
