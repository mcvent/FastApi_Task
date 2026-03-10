from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.users import UserCreate, UserResponse
from fastapi import HTTPException, status
from datetime import datetime


class CreateUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_: UserCreate) -> UserResponse:
        try:
            with self._database.session() as session:
                # Проверка на существующий username
                if self._repo.username_exists(session, user_.username):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Пользователь с username '{user_.username}' уже существует"
                    )

                # Проверка на существующий email
                if self._repo.email_exists(session, user_.email):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Пользователь с email '{user_.email}' уже существует"
                    )

                # Создание пользователя
                user_dict = user_.model_dump()
                user_dict["date_joined"] = datetime.now()

                user = self._repo.create(session, user_dict)
                session.commit()

                return UserResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при создании пользователя: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )