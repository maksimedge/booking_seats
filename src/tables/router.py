from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from cafes.models import Cafe

from .crud import create_table as create_table_crud
from .crud import get_table_by_id, get_tables_by_cafe
from .crud import update_table as update_table_crud
from .schemas import TableCreate, TableResponse, TableUpdate
from core.db import get_session

router = APIRouter(
    prefix='/cafes',
)


@router.get(
    '/{cafe_id}/tables',
    response_model=List[TableResponse],
)
async def get_tables(
    cafe_id: UUID,
    only_active: bool = Query(True, description='Только активные'),
    db: AsyncSession = Depends(get_session),
) -> List[TableResponse]:
    """Получить список столов кафе."""
    return await get_tables_by_cafe(db, cafe_id, only_active)


@router.get(
    '/{cafe_id}/tables/{table_id}',
    response_model=TableResponse,
)
async def get_table(
    cafe_id: UUID,
    table_id: UUID,
    db: AsyncSession = Depends(get_session),
) -> TableResponse:
    """Получить информацию о столе по ID."""
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
    return table


@router.post(
    '/{cafe_id}/tables',
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_table(
    cafe_id: UUID,
    table_data: TableCreate,
    db: AsyncSession = Depends(get_session),
) -> TableResponse:
    """Создать новый стол."""
    # if table_data.cafe_id != cafe_id:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail='cafe_id в URL не совпадает с cafe_id в теле запроса',
    #     )

    cafe = await db.get(Cafe, cafe_id)
    if not cafe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Кафе с ID {cafe_id} не найдено',
        )

    return await create_table_crud(db, table_data)


@router.patch(
    '/{cafe_id}/tables/{table_id}',
    response_model=TableResponse,
)
async def update_table(
    cafe_id: UUID,
    table_id: UUID,
    update_data: TableUpdate,
    db: AsyncSession = Depends(get_session),
) -> TableResponse:
    """Обновить данные стола."""
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

    if update_data.cafe_id is not None and update_data.cafe_id != cafe_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='cafe_id в URL не совпадает с cafe_id в теле запроса',
        )
    return await update_table_crud(db, table, update_data)
