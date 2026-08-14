from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from users.crud import get_user_by_login
from users.schemas import AuthData, AuthToken

from core.db import get_session
from core.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['Аутентификация'])


@router.post('/login', response_model=AuthToken)
async def login(
    auth_data: AuthData,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AuthToken:
    """Аутентифицирует пользователя по email/телефону и паролю."""
    user = await get_user_by_login(db, auth_data.login)
    if user is None or not verify_password(auth_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Неверные имя пользователя или пароль',
        )
    token = create_access_token(data={'sub': str(user.id), 'role': user.role})
    return AuthToken(access_token=token)
