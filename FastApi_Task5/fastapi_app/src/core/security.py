from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from src.exceptions import ForbiddenError

SECRET_KEY = "super-secret-key-change-me-in-production-12345"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет совпадение пароля с хешем.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Хеширует пароль алгоритмом bcrypt.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Генерирует JWT токен.
    :param data: Словарь данных для токена (обычно {'sub': username}).
    :param expires_delta: Время жизни токена. Если не указано, берется из конфига.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """
    Декодирует JWT токен и возвращает payload.
    Возвращает None если токен невалидный.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"JWT Decode Error: {e}")
        return None

def check_admin_permissions(user: dict, action: str = "выполнить это действие"):
    """Вспомогательная функция для проверки прав администратора"""
    if not user.get("is_superuser"):
        raise ForbiddenError(
            message=f"Недостаточно прав для {action}. Требуются права администратора.",
            required_role="admin",
            user_role="admin" if user.get("is_superuser") else "user"
        )