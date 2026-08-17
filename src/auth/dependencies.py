from http import HTTPStatus
from typing import Annotated, Optional

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
) -> User:
    """Возвращает текущего пользователя, если он аутентифицирован и активен."""
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Неверный или истёкший токен',
        )
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Возвращает пользователя, если он администратор."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только для администраторов',
        )
    return current_user


async def get_current_manager_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Возвращает пользователя, если он администратор или менеджер."""
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только для администраторов или менеджеров',
        )
    return current_user
