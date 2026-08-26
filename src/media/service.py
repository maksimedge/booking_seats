import uuid
from http import HTTPStatus
from io import BytesIO
from pathlib import Path

import aiofiles
from PIL import Image
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from media.constants import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_FILE_TYPES,
    BASE_DIR,
    IMAGES_DIR,
    MAX_FILE_SIZE,
    MAX_FILE_SIZE_FOR_MESSAGE,
)
from media.crud import create_media, get_media_by_id


async def upload_media(file: UploadFile, session: AsyncSession) -> uuid.UUID:
    """Загрузка изображений."""
    check_for_correct_content(file)

    media_id = uuid.uuid4()

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    file_path = IMAGES_DIR / f'{media_id}.jpg'

    relative_path = file_path.relative_to(BASE_DIR)

    content = await file.read()

    check_for_correct_size(len(content))

    jpeg_content = validate_and_convert_media(content)

    async with aiofiles.open(file_path, 'wb') as destination:
        await destination.write(jpeg_content)

    try:
        media_file = await create_media(str(relative_path), session)
    except Exception:
        delete_file(file_path)
        raise

    return media_file.id


async def get_file_path_by_id(media_id: uuid.UUID, session: AsyncSession) -> Path:
    """Возврат пути файла по айди."""
    media_file = await get_media_by_id(media_id=media_id, session=session)

    if media_file is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Изображение не найдено.',
        )

    absolute_path = BASE_DIR / media_file.path

    if not absolute_path.is_file():
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Файл не найден.',
        )

    return absolute_path


def validate_and_convert_media(content: bytes) -> bytes:
    """Проверяем и конвертируем изображение."""
    buffer = BytesIO(content)
    image = Image.open(buffer)
    if image.format not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Поддерживается загрузка только JPG или PNG.',
        )
    if image.format == 'PNG':
        image = image.convert('RGB')

    output = BytesIO()
    image.save(output, format='JPEG')

    return output.getvalue()


def check_for_correct_content(file: UploadFile) -> None:
    """Проверка на то, чтобы файл был именно изображение."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Поддерживается загрузка только изображений.',
        )


def check_for_correct_size(file_size: int) -> None:
    """Проверяем размер файла."""
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Файл не может быть более {int(MAX_FILE_SIZE_FOR_MESSAGE)} мб.',
        )


def delete_file(file_path: Path) -> None:
    """Удаление файла."""
    if file_path.exists():
        file_path.unlink()
