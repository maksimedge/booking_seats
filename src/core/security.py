from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash

from core.settings import settings

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет пароль на соответствие хешу."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Возвращает хеш пароля."""
    return password_hash.hash(password)


def create_access_token(data: dict) -> str:
    """Создаёт JWT-токен с указанными данными."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    """Декодирует JWT-токен и возвращает payload или None."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except (JWTError, ValueError, TypeError):
        return None
