from bookings.models import Booking
from cafes.models import Cafe
from media.models import Image
from tables.models import Table
from time_slots.models import TimeSlot
from users.models import User

from core.base_model import Base

__all__ = [
    'Base',
    'Image',
    'User',
    'Cafe',
    'TimeSlot',
    'Table',
    'Booking',
]
