from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from media.schemas import MediaInfo
from media.service import upload_media

router = APIRouter()


@router.post(
    '/media',
    response_model=MediaInfo,
    description=(
        'Загрузка изображения на сервер. Поддерживаются форматы jpg, png. '
        'Размер файла не более 5Мб. '
        'Только для администраторов и менеджеров'
    ),
    summary='Загрузка изображения',
)
async def upload_file(file: Annotated[UploadFile, File()]) -> MediaInfo:
    """Апи для загрузки файла."""
    return await upload_media(file)
