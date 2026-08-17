from sqlalchemy.ext.asyncio import AsyncSession

from media.models import Image


async def create_media(media_path: str, session: AsyncSession) -> Image:
    """Записываем адрес файла в БД."""
    image = Image(path=media_path)
    session.add(image)
    await session.flush()
    return image
