from fastapi import Request
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
