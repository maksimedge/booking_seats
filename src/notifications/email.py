from bookings.models import Booking


def send_email(booking: Booking) -> None:
    """Отправляем уведомление через почту."""
    # print(booking.cafe.managers)
    for item in booking.cafe.managers:
        print(item.email)
        print(item.phone)
        print(item.username)
    print(booking.cafe.name)
    print(booking.cafe.address)
    print(booking.tables_slots)
    print('I am sending notification to manager: .')
