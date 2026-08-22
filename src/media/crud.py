import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from media.models import Image


async def create_media(media_path: str, session: AsyncSession) -> Image:
    """Записываем адрес файла в БД."""
    image = Image(path=media_path)
    session.add(image)
    await session.flush()
    return image


async def get_media_by_id(media_id: uuid.UUID, session: AsyncSession) -> Image | None:
    """Читаем данные по файлу из базы."""
    result = await session.execute(select(Image).where(Image.id == media_id))

    return result.scalars().first()
