from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base


class Image(Base):
    """Модель изображения."""

    path: Mapped[str] = mapped_column(nullable=False)
