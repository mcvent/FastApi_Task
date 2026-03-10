from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.users import UserUpdate, UserResponse
from fastapi import HTTPException, status


class UpdateUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_id: int, update_: UserUpdate
    ) -> UserResponse:
        try:
            with self._database.session() as session:
                # Проверка существования пользователя
                user = self._repo.get_by_id(session, user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Пользователь с username '{user_.username}' уже существует"
                    )

                # Проверка на дубликат email (если меняется)
                if update_.email:
                    if self._repo.email_exists(session, update_.email):
                        existing_user = self._repo.get_by_email(session, update_.email)
                        if existing_user and existing_user.id != user_id:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Пользователь с email '{user_.email}' уже существует"
                            )

                # Обновление
                user = self._repo.update(session, user_id, update_.model_dump(exclude_unset=True))
                session.commit()

                return UserResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при обновлении пользователя: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )