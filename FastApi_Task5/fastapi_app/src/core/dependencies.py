from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.users import UserRepository
from src.core.security import decode_token
from src.schemas.token import TokenData
import logging

logger = logging.getLogger(__name__)

# Используем HTTPBearer для авторизации по токену
security = HTTPBearer()


async def get_db_session():
    """Асинхронная зависимость для получения сессии БД"""
    async with database.session() as session:
        yield session


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db_session)
):
    """
    Зависимость для получения текущего пользователя.
    Токен передается в заголовке Authorization: Bearer <token>
    """
    # Если нет credentials, пользователь не авторизован
    if credentials is None:
        logger.error("Попытка доступа без токена")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодируем токен
    payload = decode_token(token)

    if payload is None:
        logger.error("Невалидный токен")
        raise credentials_exception

    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None or user_id is None:
        logger.error(f"Токен не содержит sub или user_id: {payload}")
        raise credentials_exception

    # Ищем пользователя в БД
    user_repo = UserRepository()
    user = await user_repo.get_by_username(db, username)

    if user is None:
        logger.error(f"Пользователь {username} не найден в БД")
        raise credentials_exception

    if not user.is_active:
        logger.warning(f"Пользователь {username} заблокирован")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не активен"
        )

    logger.info(f"Пользователь {username} успешно авторизован")

    # Возвращаем словарь
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active
    }