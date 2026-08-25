from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Настройки приложения."""

    # Общие настройки
    title: str = 'Проект «Бронирование мест в кафе»'
    version: str = '0.0.1'
    description: str = 'Проект «Бронирование мест в кафе»'

    # Настройки подключения к БД
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_server: str = 'localhost'
    postgres_port: int = 5432

    # Настройка локации папки медиа
    images_dir: Path = Path('images')

    # Аутентификация
    secret_key: str = 'secret'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30

    # Настройки логирования
    log_level: str = 'INFO'
    log_dir: str = 'logs'
    log_file_name: str = 'app.log'
    log_rotation: str = '10 MB'
    log_retention: int = 5
    log_to_console: bool = True

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '../infra/.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @property
    def db_url(self) -> str:
        """Строка подключения к БД."""
        return (
            f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
            f'{self.postgres_server}:{self.postgres_port}/{self.postgres_db}'
        )


settings = Settings()
