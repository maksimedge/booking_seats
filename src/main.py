from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from api.router import main_router

from core.exception_handler import app_exception_handler
from core.exceptions import AppException
from core.logger import logger, setup_logging
from core.middleware import LoggingMiddleware
from core.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Жизненный цикл приложения FastAPI."""
    setup_logging()
    logger.info('Приложение "{}" запущено (версия {})', settings.title, settings.version)
    yield
    logger.info('Приложение "{}" остановлено', settings.title)


app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)


app.include_router(main_router)


@app.get('/health')
async def health() -> dict:
    """Health monitor."""
    return {'status': 'ok'}


@app.get(
    path='/',
    response_model=dict,
)
async def index() -> dict:
    """Основная страница."""
    return {
        'app': f'{settings.title} ({settings.version})',
        'description': settings.description,
        'status': 'OK',
    }


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
