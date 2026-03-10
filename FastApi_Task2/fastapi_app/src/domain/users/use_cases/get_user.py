from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.users import UserResponse, UserListResponse
from fastapi import HTTPException, status


class GetUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def get_by_id(self, user_id: int) -> UserResponse:
        try:
            with self._database.session() as session:
                user = self._repo.get_by_id(session, user_id)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Пользователь с username '{user_.username}' уже существует"
                    )
                return UserResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении пользователя по ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> UserListResponse:
        try:
            with self._database.session() as session:
                users, total = self._repo.get_all(session, skip, limit)
                return UserListResponse(
                    items=[UserResponse.model_validate(u) for u in users],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении списка пользователей: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_by_username(self, username: str) -> UserResponse:
        try:
            with self._database.session() as session:
                user = self._repo.get_by_username(session, username)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found"
                    )
                return UserResponse.model_validate(user)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении пользователя по username: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )