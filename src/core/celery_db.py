from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from core.settings import settings

celery_engine = create_async_engine(
    settings.db_url,
    poolclass=NullPool,
)

celery_session_maker = async_sessionmaker(
    bind=celery_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
