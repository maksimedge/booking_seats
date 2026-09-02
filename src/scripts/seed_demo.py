import asyncio
from pathlib import Path

import asyncpg

from core.settings import settings

SQL_FILE = Path(__file__).with_name('seed_data.sql')


async def seed_database() -> None:
    """Загружает демонстрационные данные в базу данных."""
    if not SQL_FILE.exists():
        raise FileNotFoundError(
            f'Файл seed_data.sql не найден: {SQL_FILE}',
        )

    sql = SQL_FILE.read_text(encoding='utf-8')

    connection = await asyncpg.connect(
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db,
        host=settings.postgres_server,
        port=settings.postgres_port,
    )

    try:
        await connection.execute(sql)
    finally:
        await connection.close()

    print('Демонстрационные данные успешно загружены.')


if __name__ == '__main__':
    asyncio.run(seed_database())
