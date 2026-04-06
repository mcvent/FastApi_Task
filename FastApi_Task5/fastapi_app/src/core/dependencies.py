from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.core.security import decode_token
from src.schemas.token import TokenData

# Используем HTTPBearer для авторизации по токену
security = HTTPBearer()


def get_db_session():
    """Зависимость для получения сессии БД"""
    with database.session() as session:
        yield session


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db_session)
):
    """
    Зависимость для получения текущего пользователя.
    Токен передается в заголовке Authorization: Bearer <token>
    """
    # Если нет credentials, пользователь не авторизован
    if credentials is None:
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
        raise credentials_exception

    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None or user_id is None:
        raise credentials_exception

    # Ищем пользователя в БД
    user_repo = UserRepository()
    user = user_repo.get_by_username(db, username)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не активен"
        )

    # Возвращаем словарь
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser,
        "is_active": user.is_active
    }