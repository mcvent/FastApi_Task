from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.users import UserUpdate, UserResponse
from src.exceptions import NotFoundException, ConflictError, DatabaseException, ForbiddenError
from src.core.security import get_password_hash


class UpdateUserUseCase:
    def __init__(self):
        self._database = database
        self._repo = UserRepository()

    async def execute(self, user_id: int, update_data: UserUpdate, current_user: dict) -> UserResponse:
        try:
            # Проверка: только сам пользователь может редактировать свой профиль
            if current_user.get("id") != user_id:
                raise ForbiddenError(
                    message="Вы можете редактировать только свой профиль",
                    required_role="self",
                    user_role="other_user",
                    details={"user_id": user_id, "current_user_id": current_user.get("id")}
                )

            with self._database.session() as session:
                # Проверяем существование пользователя
                existing_user = self._repo.get_by_id(session, user_id)
                if not existing_user:
                    raise NotFoundException(
                        resource="User",
                        field="id",
                        value=user_id
                    )

                # Если меняется email, проверяем уникальность
                if update_data.email is not None and update_data.email != existing_user.email:
                    if update_data.email and self._repo.email_exists(session, update_data.email):
                        raise ConflictError(
                            resource="User",
                            field="email",
                            value=update_data.email
                        )

                # Если меняется пароль - хешируем
                update_dict = update_data.model_dump(exclude_unset=True)
                if "password" in update_dict and update_dict["password"]:
                    update_dict["password"] = get_password_hash(update_dict["password"])

                # Обновляем
                updated_user = self._repo.update(session, user_id, update_dict)
                session.commit()

                return UserResponse.model_validate(updated_user)

        except (NotFoundException, ConflictError, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "UpdateUserUseCase"
            e.details["user_id"] = user_id
            e.details["current_user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при обновлении пользователя: {str(e)}",
                details={"use_case": "UpdateUserUseCase", "user_id": user_id}
            )