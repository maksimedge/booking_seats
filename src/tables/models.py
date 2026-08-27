from sqlalchemy import Column, Integer, Text, Uuid

from core.base_model import Base


class Table(Base):
    """Модель стола для бронирования в кафе."""

    __tablename__ = 'tables'

    cafe_id = Column(Uuid, nullable=False, index=True)
    seats_count = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
