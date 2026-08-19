import uuid
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from media.constants import BASE_DIR
from media.crud import get_media_by_id
from media.schemas import MediaInfo
from media.service import upload_media

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
    # dependencies=[Depends(current_superuser)]
)
async def upload_file(file: Annotated[UploadFile, File()], session: SessionDep) -> MediaInfo:
    """Апи для загрузки файла."""
    media_file_id = await upload_media(file, session)
    return MediaInfo(media_id=media_file_id)


@router.get(
    '/media/{media_id}',
)
async def get_image_by_id(media_id: uuid.UUID, session: SessionDep) -> FileResponse:
    """Ендпойнт для возврата файла по айди."""
    media_file = await get_media_by_id(media_id=media_id, session=session)

    if media_file is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Изображение не найдено.',
        )

    relative_path = media_file.path

    absolute_path = BASE_DIR / relative_path

    # TODO перенести в сервис, добавит проверку на наличие физического файла

    return FileResponse(
        path=absolute_path,
        media_type='image/jpeg',
    )
