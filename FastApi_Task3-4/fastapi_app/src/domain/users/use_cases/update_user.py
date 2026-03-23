from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.users import UserUpdate, UserResponse
from src.exceptions import NotFoundException, ConflictError, DatabaseException


class UpdateUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_id: int, update_data: UserUpdate
    ) -> UserResponse:
        try:
            with self._database.session() as session:
                user = self._repo.get_by_id(session, user_id)
                if not user:
                    raise NotFoundException(
                        resource="User",
                        field="id",
                        value=user_id
                    )

                if update_data.email:
                    if self._repo.email_exists(session, update_data.email):
                        existing = self._repo.get_by_email(session, update_data.email)
                        if existing and existing.id != user_id:
                            raise ConflictError(
                                resource="User",
                                field="email",
                                value=update_data.email
                            )

                user = self._repo.update(session, user_id, update_data.model_dump(exclude_unset=True))
                session.commit()

                return UserResponse.model_validate(user)

        except (NotFoundException, ConflictError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "UpdateUserUseCase"
            e.details["user_id"] = user_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Неожиданная ошибка при обновлении пользователя: {str(e)}",
                details={"use_case": "UpdateUserUseCase", "user_id": user_id}
            )