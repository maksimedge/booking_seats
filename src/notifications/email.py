from bookings.models import Booking


def send_email(manager_email: str, booking: Booking, updated: bool | None) -> None:
    """Отправляем уведомление через почту."""
    print('I am sending notification to manager: .')
    if updated:
        print(manager_email)
        print('___________________________________________________')
        print(f'Бронирование {booking.id} было обновлено')
        print(booking.booking_date)
        print(booking.cafe.name)
        print('___________________________________________________')
    else:
        print(manager_email)
        print('___________________________________________________')
        print(f'Бронирование {booking.id} было создано')
        print(booking.cafe.name)
        print(booking.cafe.address)
        print(booking.tables_slots)
        print('___________________________________________________')
