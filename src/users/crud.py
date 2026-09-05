from http import HTTPStatus
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.schemas import UserCreate, UserUpdate

from core.exceptions import AppException
from core.logger import logger
from core.security import get_password_hash


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """Создаёт нового пользователя с хешированным паролем.

    Проверяет уникальность username, email и phone через БД.
    """
    if await get_user_by_username(db, user_create.username):
        raise AppException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Username already exists',
        )
    if user_create.email and await get_user_by_email(db, user_create.email):
        raise AppException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Email already exists',
        )
    if user_create.phone and await get_user_by_phone(db, user_create.phone):
        raise AppException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Phone already exists',
        )

    user = User(
        username=user_create.username,
        password_hash=get_password_hash(user_create.password),
        email=user_create.email,
        phone=user_create.phone,
        tg_id=user_create.tg_id,
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        logger.info(
            'Создана запись в таблице users с параметрами: username={}, email={}, role={}',
            user.username,
            user.email,
            user.role.value,
        )
    except Exception as e:
        await db.rollback()
        logger.error('Ошибка при создании записи в таблице users: {}', e)
        raise
    return user


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Возвращает пользователя по его идентификатору."""
    return await db.get(User, user_id)


async def get_user_by_login(db: AsyncSession, login: str) -> User | None:
    """Находит пользователя по email или телефону."""
    result = await db.execute(
        select(User).where((User.email == login) | (User.phone == login)),
    )
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession) -> list[User]:
    """Возвращает список всех пользователей."""
    result = await db.execute(select(User))
    return list(result.scalars().all())


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Возвращает пользователя по username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Возвращает пользователя по email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> User | None:
    """Возвращает пользователя по телефону."""
    result = await db.execute(select(User).where(User.phone == phone))
    return result.scalar_one_or_none()


async def update_user(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
    """Обновляет данные пользователя, хешируя новый пароль при его изменении.

    Проверяет уникальность обновляемых полей (username, email, phone)
    среди других пользователей (исключая самого себя).
    """
    data = user_update.model_dump(exclude_unset=True)

    if 'username' in data and data['username'] is not None:
        existing = await get_user_by_username(db, data['username'])
        if existing and existing.id != user.id:
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Username already exists',
            )
    if 'email' in data and data['email'] is not None:
        existing = await get_user_by_email(db, data['email'])
        if existing and existing.id != user.id:
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Email already exists',
            )
    if 'phone' in data and data['phone'] is not None:
        existing = await get_user_by_phone(db, data['phone'])
        if existing and existing.id != user.id:
            raise AppException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail='Phone already exists',
            )

    # Хеширование пароля, если передан
    if 'password' in data and data['password'] is not None:
        data['password_hash'] = get_password_hash(data.pop('password'))

    for key, value in data.items():
        setattr(user, key, value)

    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
        logger.info('Обновлена запись в таблице users, id={}', user.id)
    except Exception as e:
        await db.rollback()
        logger.error('Ошибка при обновлении записи в таблице users, id={}: {}', user.id, e)
        raise
    return user
