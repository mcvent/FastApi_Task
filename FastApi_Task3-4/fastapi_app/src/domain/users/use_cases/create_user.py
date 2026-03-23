from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.users import UserCreate, UserResponse
from src.exceptions import ConflictError, DatabaseException
from datetime import datetime


class CreateUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_data: UserCreate) -> UserResponse:
        try:
            with self._database.session() as session:
                # Проверка на существующий username
                if self._repo.username_exists(session, user_data.username):
                    raise ConflictError(
                        resource="User",
                        field="username",
                        value=user_data.username
                    )

                # Проверка на существующий email
                if self._repo.email_exists(session, user_data.email):
                    raise ConflictError(
                        resource="User",
                        field="email",
                        value=user_data.email
                    )

                # Создание пользователя
                user_dict = user_data.model_dump()
                user_dict["date_joined"] = datetime.now()

                user = self._repo.create(session, user_dict)
                session.commit()

                return UserResponse.model_validate(user)

        except ConflictError:
            raise
        except DatabaseException as e:
            # Обогащаем ошибку данными из use case
            e.details["use_case"] = "CreateUserUseCase"
            e.details["username"] = user_data.username
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Неожиданная ошибка при создании пользователя: {str(e)}",
                details={"use_case": "CreateUserUseCase", "username": user_data.username}
            )