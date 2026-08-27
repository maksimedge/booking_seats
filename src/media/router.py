import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_manager_or_admin
from media.schemas import MediaInfo
from media.service import get_file_path_by_id, upload_media

from core.db import get_session

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    '/media',
    response_model=MediaInfo,
    description=(
        'Загрузка изображения на сервер. Поддерживаются форматы jpg, png. '
        'Размер файла не более 5Мб. '
        'Только для администраторов и менеджеров'
    ),
    summary='Загрузка изображения',
    dependencies=[Depends(get_current_manager_or_admin)],
)
async def upload_file(file: Annotated[UploadFile, File()], session: SessionDep) -> MediaInfo:
    """Апи для загрузки файла."""
    media_file_id = await upload_media(file, session)
    return MediaInfo(media_id=media_file_id)


@router.get(
    '/media/{media_id}',
    summary='Возвращает изображение в бинарном формате.',
    description='Возвращает изображение по айди.',
)
async def get_image_by_id(media_id: uuid.UUID, session: SessionDep) -> FileResponse:
    """Ендпойнт для возврата файла по айди."""
    file_path = await get_file_path_by_id(media_id=media_id, session=session)

    return FileResponse(
        path=file_path,
        media_type='image/jpeg',
    )
