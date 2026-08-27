from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from users.constants import UserRole
from users.crud import create_user, get_user_by_id, update_user
from users.models import User
from users.schemas import UserCreate, UserUpdate
from users.validators import check_email_unique, check_phone_unique, check_username_unique

from core.logger import logger


async def register_user_service(
    user_create: UserCreate,
    db: AsyncSession,
    current_user: User | None,
) -> User:
    """Регистрация нового пользователя с проверкой прав."""
    if current_user is not None and current_user.role == UserRole.USER:
        logger.warning('Попытка создания пользователя обычным пользователем')
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Обычный пользователь не может создавать новых пользователей',
        )

    await check_username_unique(db, user_create.username)
    await check_email_unique(db, user_create.email)
    await check_phone_unique(db, user_create.phone)

    return await create_user(db, user_create)


async def update_me_service(
    user_update: UserUpdate,
    db: AsyncSession,
    current_user: User,
) -> User:
    """Обновление собственного профиля."""
    if user_update.role is not None and user_update.role != current_user.role:
        logger.warning('Попытка изменения роли самому себе')
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Нельзя изменить роль самому себе',
        )
    if user_update.is_active is not None and user_update.is_active != current_user.is_active:
        logger.warning('Попытка изменения собственной активности')
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Нельзя изменить собственную активность',
        )

    await check_username_unique(db, user_update.username, exclude_user_id=current_user.id)
    await check_email_unique(db, user_update.email, exclude_user_id=current_user.id)
    await check_phone_unique(db, user_update.phone, exclude_user_id=current_user.id)

    return await update_user(db, current_user, user_update)


async def get_user_service(
    user_id: int,
    db: AsyncSession,
    current_user: User,
) -> User:
    """Получение пользователя по ID с проверкой прав."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не найден',
        )
    if current_user.role == UserRole.USER and user.id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только к своей записи',
        )
    return user


async def update_user_by_id_service(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession,
    current_user: User,
) -> User:
    """Обновление пользователя по ID (админ/менеджер может менять любого, обычный — только себя)."""
    user = await get_user_by_id(db, user_id)
    if user is None:
        logger.warning('Попытка изменения несуществующего пользователя, id={}', user_id)
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Пользователь не найден',
        )

    # Проверка прав доступа
    if current_user.role == UserRole.USER and user.id != current_user.id:
        logger.warning('Отказано в изменении пользователя id={}: недостаточно прав', user_id)
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Доступ только к своей записи',
        )

    # Дополнительная защита для обычного пользователя: запрет изменения роли и активности
    if current_user.role == UserRole.USER:
        if user_update.role is not None or user_update.is_active is not None:
            logger.warning('Попытка изменения роли или активности самому себе через /{user_id}')
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail='Нельзя изменять роль или активность',
            )

    # Логирование блокировки/разблокировки
    if user_update.is_active is not None and user_update.is_active != user.is_active:
        if user_update.is_active:
            logger.info('Пользователь id={} разблокирован', user_id)
        else:
            logger.info('Пользователь id={} заблокирован', user_id)

    # Логирование изменения роли
    if user_update.role is not None and user_update.role != user.role:
        logger.info(
            'Изменена роль пользователя id={}: {} -> {}',
            user_id,
            user.role.value,
            user_update.role.value,
        )

    await check_username_unique(db, user_update.username, exclude_user_id=user_id)
    await check_email_unique(db, user_update.email, exclude_user_id=user_id)
    await check_phone_unique(db, user_update.phone, exclude_user_id=user_id)

    return await update_user(db, user, user_update)
