import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.logger import logger, reset_log_context


class LoggingMiddleware(BaseHTTPMiddleware):
    """Логирование HTTP-запросов."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Обрабатывает HTTP-запрос и логирует его."""
        start_time = time.monotonic()

        logger.info(
            'Запрос: {} {}',
            request.method,
            request.url.path,
        )

        try:
            response = await call_next(request)
        except Exception:
            logger.exception('Ошибка при обработке запроса')
            reset_log_context()
            raise

        duration = (time.monotonic() - start_time) * 1000

        logger.info(
            'Ответ: {} {} | status={} | {:.1f} мс',
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        reset_log_context()

        return response
