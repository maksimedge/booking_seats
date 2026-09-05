from collections.abc import Callable
from http import HTTPStatus
from typing import Annotated, Any, Optional
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from users.constants import STAFF_USER, UserRole
from users.crud import get_user_by_id
from users.models import User

from core.db import get_session
from core.exceptions import AppException
from core.logger import logger, set_log_context
from core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: SessionDep,
) -> User | None:
    """Возвращает пользователя, если токен валиден, иначе None."""
    if credentials is None:
        logger.debug('Отсутствующий Bearer token')
        return None

    token = credentials.credentials
    payload = decode_access_token(token)
    print(f'this is payload: {payload}')
    if payload is None:
        logger.warning('Получен невалидный токен авторизации')
        return None

    user_id = payload.get('sub')
    if user_id is None:
        logger.warning('В токене отсутствует sub')
        return None

    try:
        user_id_uuid = UUID(user_id)
    except (TypeError, ValueError):
        logger.warning('Некорректный идентификатор пользователя в токене')
        return None

    user = await get_user_by_id(db, user_id_uuid)
    if user is None:
        logger.warning('Пользователь по токену не найден')
        return None

    set_log_context(user_id=user.id, username=user.username)
    return user


def role_required(*allowed_roles: UserRole, allow_anon: bool = False) -> Callable[..., Any]:
    """Фабрика зависимостей, проверяющая аутентификацию и роль пользователя."""

    async def check_role(user: User | None = Depends(get_optional_current_user)) -> User | None:
        if allow_anon and user is None:
            return None

        if user is None:
            logger.warning('Попытка доступа без токена')
            raise AppException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Неверный или истёкший токен',
            )

        if not user.is_active:
            logger.warning('Попытка доступа заблокированного пользователя')
            raise AppException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Недостаточно прав',
            )

        if allowed_roles and user.role not in allowed_roles:
            logger.warning('Отказано в доступе: недостаточно прав')
            raise AppException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Недостаточно прав',
            )

        set_log_context(user_id=user.id, username=user.username)
        return user

    return check_role


get_current_active_user = role_required(allow_anon=False)
get_current_admin = role_required(UserRole.ADMIN)
get_current_manager_or_admin = role_required(*STAFF_USER)
