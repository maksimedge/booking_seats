from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from users.crud import get_user_by_login
from users.schemas import AuthData, AuthToken

from core.db import get_session
from core.logger import logger
from core.security import create_access_token, verify_password

router = APIRouter(prefix='/auth')


@router.post(
    '/login',
    response_model=AuthToken,
    summary='Получение токена авторизации',
)
async def login(
    auth_data: AuthData,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> AuthToken:
    """Аутентифицирует пользователя по email/телефону и паролю."""
    user = await get_user_by_login(db, auth_data.login)
    if user is None:
        logger.warning(
            'Неудачная попытка авторизации: пользователь с указанным email или телефоном не найден',
        )
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Неверные имя пользователя или пароль',
        )
    if not verify_password(auth_data.password, user.password_hash):
        logger.warning('Неудачная попытка авторизации: неверный пароль')
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Неверные имя пользователя или пароль',
        )
    if not user.is_active:
        logger.warning('Попытка авторизации заблокированного пользователя')
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail='Неверные имя пользователя или пароль',
        )
    token = create_access_token(data={'sub': str(user.id), 'role': user.role.value})
    logger.info('Пользователь успешно авторизован')
    return AuthToken(access_token=token)
