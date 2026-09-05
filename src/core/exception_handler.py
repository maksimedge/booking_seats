from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# from main import app
from core.exceptions import AppException


# @app.exception_handler(AppException)
async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Настройка возвращаемой ошибки."""
    if not isinstance(exc, AppException):
        raise exc
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'code': exc.status_code,
            'message': exc.message,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обработчик ошибок валидации Pydantic."""
    errors = exc.errors()
    error = errors[0]
    msg = error.get('msg', 'Ошибка валидации')

    if msg.startswith('Value error, '):
        msg = msg.replace('Value error, ', '')

    if 'json' in error.get('type', ''):
        msg = 'Неверный формат заполнения'

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'code': status.HTTP_422_UNPROCESSABLE_ENTITY,
            'message': msg,
        },
    )
