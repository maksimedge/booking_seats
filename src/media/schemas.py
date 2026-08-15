from uuid import UUID

from pydantic import BaseModel


class MediaInfo(BaseModel):
    """Схема возврата для изображений."""

    media_id: UUID
