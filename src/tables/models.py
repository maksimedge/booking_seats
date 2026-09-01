from sqlalchemy import Column, ForeignKey, Integer, Text, Uuid
from sqlalchemy.orm import relationship

from core.base_model import Base


class Table(Base):
    """Модель стола для бронирования в кафе."""

    __tablename__ = 'tables'

    cafe_id = Column(Uuid, ForeignKey('cafes.id', ondelete='CASCADE'), nullable=False, index=True)
    seat_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    cafe = relationship('Cafe', lazy='joined')
