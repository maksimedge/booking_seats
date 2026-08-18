"""Централизованное логирование приложения на основе Loguru.

Использование в других слоях (CRUD/бизнес-логика):

    from core.logger import logger, log_action

    logger.info('Пользователь заблокирован')
    log_action('Создана запись', table='bookings', booking_id=booking.id, user_id=user.id)

Чтобы в логах запроса отображался username/id текущего пользователя (а не SYSTEM),
нужно один раз вызвать `set_log_context(user_id, username)` внутри зависимости
аутентификации (например, `get_current_user` в модуле `auth`) сразу после
успешной проверки JWT-токена:

    from core.logger import set_log_context

    async def get_current_user(...) -> User:
        user = ...  # проверка токена и получение пользователя из БД
        set_log_context(user_id=user.id, username=user.username)
        return user

Если контекст не установлен (запрос анонимный или лог пишется вне запроса,
например при старте приложения), в логе будет указано `user=SYSTEM`.
"""

import sys
from contextvars import ContextVar
from pathlib import Path
from typing import Any

from loguru import logger as _logger

from core.settings import BASE_DIR, settings

SYSTEM_USER = 'SYSTEM'

_user_ctx: ContextVar[dict[str, Any] | None] = ContextVar('log_user_ctx', default=None)

_LOG_FORMAT_CONSOLE = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    'user=<cyan>{extra[username]}</cyan> (id=<cyan>{extra[user_id]}</cyan>) | '
    '<level>{message}</level>'
)

_LOG_FORMAT_FILE = (
    '{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | user={extra[username]} (id={extra[user_id]}) | {message}'
)


def set_log_context(user_id: Any = None, username: str | None = None) -> None:
    """Устанавливает данные текущего пользователя в контекст логирования.

    Все записи лога, сделанные в рамках текущего asyncio-запроса после вызова
    этой функции, будут содержать переданные `user_id`/`username`.
    """
    if user_id is None and username is None:
        _user_ctx.set(None)
        return
    _user_ctx.set(
        {
            'user_id': str(user_id) if user_id is not None else '-',
            'username': username or SYSTEM_USER,
        },
    )


def reset_log_context() -> None:
    """Сбрасывает контекст пользователя (например, после завершения запроса)."""
    _user_ctx.set(None)


def _patch_record(record: dict[str, Any]) -> None:
    """Дополняет запись лога данными текущего пользователя (или SYSTEM)."""
    user = _user_ctx.get()
    record['extra'].setdefault('username', user['username'] if user else SYSTEM_USER)
    record['extra'].setdefault('user_id', user['user_id'] if user else '-')


def setup_logging() -> None:
    """Настраивает централизованное логирование: вывод в консоль и в файл с ротацией.

    Схема ротации соответствует ТЗ: используется один активный файл лога и
    `settings.log_retention - 1` архивных. Как только активный файл достигает
    размера `settings.log_rotation`, он переводится в архив, а самый старый
    архивный файл (если общее количество файлов превышает `settings.log_retention`)
    удаляется.
    """
    _logger.remove()
    _logger.configure(patcher=_patch_record)

    if settings.log_to_console:
        _logger.add(
            sys.stdout,
            level=settings.log_level,
            format=_LOG_FORMAT_CONSOLE,
            colorize=True,
            backtrace=False,
            diagnose=False,
        )

    log_dir = Path(BASE_DIR) / settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / settings.log_file_name

    _logger.add(
        log_file_path,
        level=settings.log_level,
        format=_LOG_FORMAT_FILE,
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        encoding='utf-8',
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    _logger.info(
        'Логирование настроено: console={}, file={}',
        settings.log_to_console,
        log_file_path,
    )


def log_action(action: str, table: str | None = None, **params: Any) -> None:
    """Логирует бизнес-действие (создание/изменение записи и т.п.) в едином формате.

    Пример:
        log_action('Создана запись', table='bookings', booking_id=booking.id)
        # -> "Создана запись в таблице bookings с параметрами: booking_id=..."
    """
    message = action
    if table:
        message += f' в таблице {table}'
    if params:
        details = ', '.join(f'{key}={value}' for key, value in params.items())
        message += f' с параметрами: {details}'
    _logger.info(message)


logger = _logger

__all__ = [
    'log_action',
    'logger',
    'reset_log_context',
    'set_log_context',
    'setup_logging',
]
