from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from users.crud import get_user_by_id
from users.models import User

from core.db import get_session
from core.security import decode_access_token

bearer_scheme = HTTPBearer()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: SessionDep,
) -> User:
    """Возвращает текущего пользователя по JWT-токену."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный или истёкший токен',
        )
    user_id = payload.get('sub')
    if user_id is None:
        raise HTTPException(status_code=401, detail='Некорректный токен')
    user = await get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail='Пользователь не найден или неактивен')
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Возвращает пользователя, если он администратор."""
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail='Доступ только для администраторов')
    return current_user


async def get_current_manager_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Возвращает пользователя, если он администратор или менеджер."""
    if current_user.role not in ('ADMIN', 'MANAGER'):
        raise HTTPException(status_code=403, detail='Доступ только для администраторов или менеджеров')
    return current_user
