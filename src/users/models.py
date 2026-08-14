from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.base_model import Base


class User(Base):
    """Модель пользователя системы бронирования."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    tg_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    role: Mapped[str] = mapped_column(String(20), default='USER', server_default='USER')
