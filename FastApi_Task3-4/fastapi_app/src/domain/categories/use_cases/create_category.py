from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate, CategoryResponse
from src.exceptions import ConflictError, DatabaseException
from datetime import datetime

class CreateCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_data: CategoryCreate) -> CategoryResponse:
        try:
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

        except ConflictError:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreateCategoryUseCase"
            e.details["slug"] = category_data.slug
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при создании категории: {str(e)}",
                details={"use_case": "CreateCategoryUseCase", "slug": category_data.slug}
            )