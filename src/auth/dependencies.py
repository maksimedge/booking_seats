from collections.abc import Callable
from http import HTTPStatus
from typing import Annotated, Any, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from users.constants import STAFF_USER, UserRole
from users.crud import get_user_by_id
from users.models import User

from core.db import get_session
from core.logger import logger
from core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: SessionDep,
) -> User | None:
    """Возвращает пользователя, если токен валиден, иначе None."""
    if credentials is None:
        logger.warning('Отсутствующий Bearer token')
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        logger.warning('Получен невалидный токен авторизации')
        return None
    user_id = payload.get('sub')
    if user_id is None:
        logger.warning('Пользователь по токену не найден')
        return None
    try:
        user_id_int = int(user_id)
    except (TypeError, ValueError):
        logger.warning('Некорректный идентификатор пользователя в токене')
        return None
    return await get_user_by_id(db, user_id_int)


def role_required(*allowed_roles: UserRole, allow_anon: bool = False) -> Callable[..., Any]:
    """ЗависимостИ для проверки аутентификации и роли."""

    async def check_role(user: User | None = Depends(get_optional_current_user)) -> User | None:
        if allow_anon and user is None:
            return None
        if user is None or not user.is_active:
            logger.warning('Попытка авторизации заблокированного пользователя или отсутствует токен')
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Неверный или истёкший токен',
            )
        if user.role not in allowed_roles:
            logger.warning('Отказано в доступе: недостаточно прав')
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Недостаточно прав',
            )
        return user

    return check_role


get_current_active_user = role_required(allow_anon=False)
get_current_admin = role_required(UserRole.ADMIN)
get_current_manager_or_admin = role_required(*STAFF_USER)
