from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging
logger = logging.getLogger(__name__)

class DeleteUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_id: int, current_user: dict) -> bool:
        try:
            # Проверка: сам пользователь или админ могут удалять
            is_self = current_user.get("id") == user_id
            is_admin = current_user.get("is_superuser", False)

            if not (is_self or is_admin):
                raise ForbiddenError(
                    message="Только хозяин или администратор можете удалить аккаунт",
                    required_role="self_or_admin",
                    user_role="admin" if is_admin else "self" if is_self else "other",
                    details={"user_id": user_id, "current_user_id": current_user.get("id")}
                )

            with self._database.session() as session:
                user = self._repo.get_by_id(session, user_id)
                if not user:
                    raise NotFoundException(
                        resource="User",
                        field="id",
                        value=user_id
                    )

                success = self._repo.delete(session, user_id)
                session.commit()
                return success

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteUserUseCase"
            e.details["user_id"] = user_id
            e.details["current_user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении пользователя: {str(e)}",
                details={"use_case": "DeleteUserUseCase", "user_id": user_id}
            )