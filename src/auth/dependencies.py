from http import HTTPStatus
from typing import Annotated, Any, Callable, Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from users.constants import UserRole
from users.crud import get_user_by_id
from users.models import User

from core.db import get_session
from core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_optional_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: SessionDep,
) -> User | None:
    """Возвращает пользователя, если токен валиден, иначе None."""
    if credentials is None:
        return None
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        return None
    user_id = payload.get('sub')
    if user_id is None:
        return None
    return await get_user_by_id(db, int(user_id))


async def get_current_user(
    user: User | None = Depends(get_optional_current_user),
) -> User | None:
    """Низкоуровневая зависимость: возвращает пользователя или None без проверки прав."""
    return user


def role_required(*allowed_roles: UserRole) -> Callable[..., Any]:
    """Фабрика зависимостей, проверяющая аутентификацию и роль пользователя."""

    async def check_role(user: User | None = Depends(get_current_user)) -> User:
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='Неверный или истёкший токен',
            )
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Недостаточно прав',
            )
        return user

    return check_role


get_current_admin = role_required(UserRole.ADMIN)
get_current_manager_or_admin = role_required(UserRole.ADMIN, UserRole.MANAGER)
