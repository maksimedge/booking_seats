import smtplib
from email.message import EmailMessage

from core.logger import logger
from core.settings import settings


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """Отправка письма."""
    message = EmailMessage()

    message['From'] = settings.email_from_address
    message['To'] = recipient
    message['Subject'] = subject

    message.set_content(body)
    try:
        with smtplib.SMTP('mailpit', 1025) as smtp:
            smtp.send_message(message)
            logger.info('Письмо {} было отправлено на адрес {}.', subject, recipient)
    except (smtplib.SMTPException, OSError):
        logger.exception('Ошибка отправки письма')
        raise
