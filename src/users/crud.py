from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from users.schemas import UserCreate, UserUpdate

from core.security import get_password_hash


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """Создаёт нового пользователя с хешированным паролем."""
    user = User(
        username=user_create.username,
        password_hash=get_password_hash(user_create.password),
        email=user_create.email,
        phone=user_create.phone,
        tg_id=user_create.tg_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
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


async def update_user(db: AsyncSession, user: User, user_update: UserUpdate) -> User:
    """Обновляет данные пользователя, хешируя новый пароль при его изменении."""
    data = user_update.model_dump(exclude_unset=True)
    if 'password' in data and data['password'] is not None:
        data['password_hash'] = get_password_hash(data.pop('password'))
    for key, value in data.items():
        setattr(user, key, value)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
