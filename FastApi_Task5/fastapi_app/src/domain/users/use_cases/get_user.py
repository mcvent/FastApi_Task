from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.users import UserRepository
from src.schemas.users import UserResponse, UserListResponse
from src.exceptions import NotFoundException, DatabaseException
import logging

logger = logging.getLogger(__name__)


class GetUserUseCase:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def get_by_id(self, session: AsyncSession, user_id: int) -> UserResponse:
        try:
            user = await self._repo.get_by_id(session, user_id)
            if not user:
                raise NotFoundException(
                    resource="User",
                    field="id",
                    value=user_id
                )
            return UserResponse.model_validate(user)
        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetUserUseCase"
            e.details["method"] = "get_by_id"
            e.details["user_id"] = user_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя: {str(e)}",
                details={"use_case": "GetUserUseCase", "user_id": user_id}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> UserListResponse:
        try:
            users, total = await self._repo.get_all(session, skip, limit)
            return UserListResponse(
                items=[UserResponse.model_validate(u) for u in users],
                total=total
            )
        except DatabaseException as e:
            e.details["use_case"] = "GetUserUseCase"
            e.details["method"] = "get_all"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка пользователей: {str(e)}",
                details={"use_case": "GetUserUseCase"}
            )

    async def get_by_username(self, session: AsyncSession, username: str) -> UserResponse:
        try:
            user = await self._repo.get_by_username(session, username)
            if not user:
                raise NotFoundException(
                    resource="User",
                    field="username",
                    value=username
                )
            return UserResponse.model_validate(user)
        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetUserUseCase"
            e.details["method"] = "get_by_username"
            e.details["username"] = username
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении пользователя по username: {str(e)}",
                details={"use_case": "GetUserUseCase", "username": username}
            )

    async def get_active_users(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> UserListResponse:
        try:
            users, total = await self._repo.get_active_users(session, skip, limit)
            return UserListResponse(
                items=[UserResponse.model_validate(u) for u in users],
                total=total
            )
        except DatabaseException as e:
            e.details["use_case"] = "GetUserUseCase"
            e.details["method"] = "get_active_users"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка активных пользователей: {str(e)}",
                details={"use_case": "GetUserUseCase", "method": "get_active_users"}
            )

    async def get_by_email(self, session: AsyncSession, email: str) -> UserResponse:
        try:
            user = await self._repo.get_by_email(session, email)
            if not user:
                raise NotFoundException(
                    resource="User",
                    field="email",
                    value=email
                )
            return UserResponse.model_validate(user)
        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetUserUseCase"
            e.details["method"] = "get_by_email"
            e.details["email"] = email
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Неожиданная ошибка при получении пользователя по email: {str(e)}",
                details={"use_case": "GetUserUseCase", "method": "get_by_email", "email": email}
            )