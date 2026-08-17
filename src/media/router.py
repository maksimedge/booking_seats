from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

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
