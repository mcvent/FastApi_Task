from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate, CategoryResponse
from src.exceptions import ConflictError, DatabaseException, ForbiddenError
from datetime import datetime
import logging
logger = logging.getLogger(__name__)


class CreateCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_data: CategoryCreate, current_user: dict) -> CategoryResponse:
        try:
            # Проверка прав: только суперпользователь
            if not current_user.get("is_superuser"):
                raise ForbiddenError(
                    message="Только суперпользователи могут создавать категории",
                    required_role="superuser",
                    user_role="user" if not current_user.get("is_superuser") else "superuser"
                )

            with self._database.session() as session:
                # Проверка на существующий slug через репозиторий (бизнес-логика)
                if self._repo.slug_exists(session, category_data.slug):
                    raise ConflictError(
                        resource="Category",
                        field="slug",
                        value=category_data.slug
                    )

                category_dict = category_data.model_dump()
                category_dict["created_at"] = datetime.now()

                category = self._repo.create(session, category_dict)
                session.commit()

                return CategoryResponse.model_validate(category)

        except (ConflictError, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreateCategoryUseCase"
            e.details["slug"] = category_data.slug
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при создании категории: {str(e)}",
                details={"use_case": "CreateCategoryUseCase", "slug": category_data.slug}
            )