from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.exceptions import NotFoundException, DatabaseException


class DeleteUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_id: int) -> bool:
        try:
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

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteUserUseCase"
            e.details["user_id"] = user_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении пользователя: {str(e)}",
                details={"use_case": "DeleteUserUseCase", "user_id": user_id}
            )