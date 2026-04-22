from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryUpdate, CategoryResponse
from src.exceptions import NotFoundException, ConflictError, DatabaseException, ForbiddenError
import logging
logger = logging.getLogger(__name__)


class UpdateCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_id: int, update_data: CategoryUpdate, current_user: dict) -> CategoryResponse:
        try:
            # Проверка прав: только суперпользователь
            if not current_user.get("is_superuser"):
                raise ForbiddenError(
                    message="Только суперпользователи могут обновлять категории",
                    required_role="superuser",
                    user_role="user" if not current_user.get("is_superuser") else "superuser"
                )

            with self._database.session() as session:
                # Проверяем существование категории
                existing_category = self._repo.get_by_id(session, category_id)
                if not existing_category:
                    raise NotFoundException(
                        resource="Category",
                        field="id",
                        value=category_id
                    )

                # Если меняется slug, проверяем уникальность
                if update_data.slug is not None and update_data.slug != existing_category.slug:
                    if self._repo.slug_exists(session, update_data.slug):
                        raise ConflictError(
                            resource="Category",
                            field="slug",
                            value=update_data.slug
                        )

                category = self._repo.update(
                    session,
                    category_id,
                    update_data.model_dump(exclude_unset=True)
                )
                session.commit()

                return CategoryResponse.model_validate(category)

        except (NotFoundException, ConflictError, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "UpdateCategoryUseCase"
            e.details["category_id"] = category_id
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при обновлении категории: {str(e)}",
                details={"use_case": "UpdateCategoryUseCase", "category_id": category_id}
            )