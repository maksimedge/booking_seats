import uuid
from http import HTTPStatus
from io import BytesIO
from pathlib import Path

import aiofiles
from PIL import Image
from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from media.constants import (
    ALLOWED_CONTENT_TYPES,
    ALLOWED_IMAGE_TYPES,
    BASE_DIR,
    IMAGES_DIR,
    MAX_FILE_SIZE,
    MAX_FILE_SIZE_FOR_MESSAGE,
)
from media.crud import create_media, get_media_by_id

from core.logger import logger

CHUNK_SIZE = 1024 * 1024  # 1mb


async def upload_media(file: UploadFile, session: AsyncSession) -> uuid.UUID:
    """Загрузка изображений."""
    check_for_correct_content(file)

    media_id = uuid.uuid4()

    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    file_path = IMAGES_DIR / f'{media_id}.jpg'

    relative_path = file_path.relative_to(BASE_DIR)

    content = await read_file_with_size_limit(file)

    jpeg_content = validate_and_convert_media(content)

    try:
        async with aiofiles.open(file_path, 'wb') as destination:
            await destination.write(jpeg_content)

    except OSError as error:
        logger.exception('Не удалось сохранить файл: {}', file_path)

        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail='Не удалось сохранить изображение',
        ) from error

    try:
        media_file = await create_media(str(relative_path), session)
        await session.commit()
        logger.info('Файл c ID:{} был сохранен по адресу: {}', media_file.id, file_path)
    except SQLAlchemyError as error:
        await session.rollback()

        logger.exception('Не удалось сохранить файл в БД: {}', file_path)
        try:
            delete_file(file_path)
        except OSError:
            logger.exception('Не удалось удалить файл после ошибки БД: {}', file_path)

        raise HTTPException(
            status_code=500,
            detail='Не удалось сохранить изображение',
        ) from error
    return media_file.id


async def get_file_path_by_id(media_id: uuid.UUID, session: AsyncSession) -> Path:
    """Возврат пути файла по айди."""
    media_file = await get_media_by_id(media_id=media_id, session=session)

    if media_file is None:
        logger.error('Изображение {} не найдено в базе данных.', media_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Изображение не найдено.',
        )

    absolute_path = BASE_DIR / media_file.path

    if not absolute_path.is_file():
        logger.error('Файл с id:{} - не найден.', media_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Файл не найден.',
        )

    return absolute_path


def validate_and_convert_media(content: bytes) -> bytes:
    """Проверяем и конвертируем изображение."""
    buffer = BytesIO(content)
    image = Image.open(buffer)
    if image.format not in ALLOWED_IMAGE_TYPES:
        logger.warning('Загрузка изображения типа {}.', image.format)
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
        logger.warning('Загружаемый файл - не изображение:{}', file.content_type)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Поддерживается загрузка только изображений.',
        )


async def read_file_with_size_limit(file: UploadFile) -> bytes:
    """Проверяем размер файла."""
    total_size = 0
    parts = []

    while True:
        part = await file.read(CHUNK_SIZE)

        if not part:
            break
        total_size += len(part)

        if total_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=f'Файл не может быть более {int(MAX_FILE_SIZE_FOR_MESSAGE)} мб.',
            )
        parts.append(part)

    return b''.join(parts)


def delete_file(file_path: Path) -> None:
    """Удаление файла."""
    if file_path.exists():
        file_path.unlink()
