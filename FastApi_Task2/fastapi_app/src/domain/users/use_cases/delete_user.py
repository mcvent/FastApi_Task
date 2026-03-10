from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from fastapi import HTTPException, status


class DeleteUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_id: int) -> bool:
        try:
            with self._database.session() as session:
                # Проверка существования пользователя
                user = self._repo.get_by_id(session, user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Пользователь с username '{user_.username}' уже существует"
                    )

                success = self._repo.delete(session, user_id)
                session.commit()
                return success

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при удалении пользователя: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
