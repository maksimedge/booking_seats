from bookings.models import Booking


def send_email(manager_email: str, booking: Booking, updated: bool | None) -> None:
    """Отправляем уведомление через почту."""
    print('I am sending notification to manager: .')
    print(manager_email, updated, '<-updated')
    if updated:
        print(manager_email)
        print(f'Бронирование {booking.id} было обновлено')
        print(booking.cafe.name)
    print(manager_email)
    print(f'Бронирование {booking.id} было создано')
    print(booking.cafe.name)
    print(booking.cafe.address)
    print(booking.tables_slots)
