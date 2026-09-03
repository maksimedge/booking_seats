import smtplib
from datetime import datetime, timedelta
from http import HTTPStatus
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import HTTPException

from bookings.crud import get_booking_with_relations, get_bookings_for_reminders
from bookings.models import Booking, BookingTableSlot
from notifications.email import send_email

from core import alembic_models  # noqa
from core.celery_db import celery_session_maker
from core.logger import logger
from core.settings import settings

TALLINN_TZ = ZoneInfo('Europe/Tallinn')


async def send_notification(booking_id: UUID, updated: bool) -> None:
    """Отправка уведомлений о создании или обновлении бронирования, менеджерам кафе."""
    async with celery_session_maker() as session:
        booking = await get_booking_with_relations(session, booking_id)

        if booking is None:
            logger.error('Бронирование {} не найдено в базе данных.', booking_id)
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail='Бронирование не найдено.',
            )

        earliest_slot = find_earliest_slot(booking.tables_slots)

        for manager in booking.cafe.managers:
            if manager.email is None:
                logger.warning('У менеджера {} не указан email', manager.id)
                continue
            mail_subject, body = build_booking_email(booking, earliest_slot, updated)

            send_email(recipient=manager.email, subject=mail_subject, body=body)


async def find_booking_for_notification() -> None:
    """Найти бронирования, которым необходимо отправить напоминамние и отпрваить его."""
    async with celery_session_maker() as session:
        bookings = await get_bookings_for_reminders(session)

        for booking in bookings:
            earliest_slot = find_earliest_slot(booking.tables_slots)

            booking_time = datetime.combine(
                booking.booking_date,
                earliest_slot.slot.start_time,
                tzinfo=TALLINN_TZ,
            )
            reminder_time = booking_time - timedelta(
                hours=settings.reminder_before_period_hours,
            )
            reminder_sent = booking.notification_sent
            subject, body = build_reminder_email(booking, earliest_slot)

            if reminder_time <= datetime.now(TALLINN_TZ) < booking_time and not reminder_sent:
                if booking.user.email is None:
                    logger.warning('У пользователя {} не указан email', booking.user.username)
                    continue

                try:
                    send_email(booking.user.email, subject, body)
                except (smtplib.SMTPException, OSError):
                    logger.exception('Ошибка отправки уведомления')
                    raise
                else:
                    booking.notification_sent = True
                    await session.commit()


def find_earliest_slot(booking_slots: list[BookingTableSlot]) -> BookingTableSlot:
    """Находит самый ранний слот у бронирования."""
    return min(
        booking_slots,
        key=lambda item: item.slot.start_time,
    )


def build_booking_email(
    booking: Booking,
    earliest_slot: BookingTableSlot,
    updated: bool,
) -> tuple[str, str]:
    """Собираем текст письма для уведомления."""
    if updated:
        subject = f'Бронирование {booking.id} в {booking.cafe.name} было обновлено.'
        body = (
            f'Бронирование {booking.id} в кафе {booking.cafe.name} было обновлено.\n'
            f'Дата: {booking.booking_date}\n'
            f'Стол: {earliest_slot.table.description} '
            f'с количеством мест: {earliest_slot.table.seat_number}\n'
            f'Количество гостей: {booking.guest_number}\n'
            f'Время начала: {earliest_slot.slot.start_time}\n'
            f'Контактные данные: почта {booking.user.email}, телефон {booking.user.phone}'
        )
        return subject, body
    subject = f'Новое бронирование в {booking.cafe.name}'
    body = (
        f'В кафе {booking.cafe.name} было сделано новое бронирование.\n'
        f'Дата: {booking.booking_date}\n'
        f'Стол: {earliest_slot.table.description} '
        f'с количеством мест: {earliest_slot.table.seat_number}\n'
        f'Количество гостей: {booking.guest_number}\n'
        f'Время начала: {earliest_slot.slot.start_time}\n'
        f'Контактные данные: почта {booking.user.email}, телефон {booking.user.phone}'
    )
    return subject, body


def build_reminder_email(booking: Booking, earliest_slot: BookingTableSlot) -> tuple[str, str]:
    """Собираем текст письма для напоминания."""
    subject = f'Напоминание о бронировании в {booking.cafe.name}.'
    body = (
        f'Напоминаем, что у вас сделано бронирование в кафе {booking.cafe.name}.\n'
        f'Дата: {booking.booking_date}\n'
        f'Стол: {earliest_slot.table.description} '
        f'с количеством мест: {earliest_slot.table.seat_number}\n'
        f'Количество гостей: {booking.guest_number}\n'
        f'Время начала: {earliest_slot.slot.start_time}'
    )
    return subject, body
