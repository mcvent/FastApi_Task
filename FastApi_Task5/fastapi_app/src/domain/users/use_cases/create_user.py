from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.users import UserRepository
from src.schemas.users import UserCreate, UserResponse
from src.exceptions import ConflictError, DatabaseException
from src.core.security import get_password_hash
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CreateUserUseCase:
    def __init__(self, session: AsyncSession, repo: UserRepository):
        self._session = session
        self._repo = repo

    async def execute(self, user_data: UserCreate, is_public: bool = True) -> UserResponse:
        """
        Создание пользователя.
        is_public=True - публичная регистрация (без проверки прав)
        """
        try:
            # Проверка на существующий username
            if await self._repo.username_exists(self._session, user_data.username):
                raise ConflictError(
                    resource="User",
                    field="username",
                    value=user_data.username
                )

            # Проверка на существующий email (если указан)
            if user_data.email and await self._repo.email_exists(self._session, user_data.email):
                raise ConflictError(
                    resource="User",
                    field="email",
                    value=user_data.email
                )

            # Создаем пользователя
            user_dict = user_data.model_dump()
            user_dict["password"] = get_password_hash(user_data.password)
            user_dict["date_joined"] = datetime.now()

            # Убираем None значения для обязательных полей
            if not user_dict.get("email"):
                user_dict["email"] = ""
            if not user_dict.get("first_name"):
                user_dict["first_name"] = ""
            if not user_dict.get("last_name"):
                user_dict["last_name"] = ""

            new_user = await self._repo.create(self._session, user_dict)
            await self._session.commit()

            return UserResponse.model_validate(new_user)

        except ConflictError:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreateUserUseCase"
            e.details["username"] = user_data.username
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при создании пользователя: {str(e)}",
                details={"use_case": "CreateUserUseCase", "username": user_data.username}
            )