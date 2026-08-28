from sqlalchemy import Column, Integer, Text

from core.base_model import Base


class Table(Base):
    """Модель стола для бронирования в кафе."""

    __tablename__ = 'tables'

    cafe_id = Column(Integer, nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
