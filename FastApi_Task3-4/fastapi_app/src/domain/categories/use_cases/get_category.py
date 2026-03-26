from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryResponse, CategoryListResponse
from src.exceptions import NotFoundException, DatabaseException

class GetCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def get_by_id(self, category_id: int) -> CategoryResponse:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_id(session, category_id)
                if not category:
                    raise NotFoundException(
                        resource="Category",
                        field="id",
                        value=category_id
                    )
                return CategoryResponse.model_validate(category)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetCategoryUseCase"
            e.details["method"] = "get_by_id"
            e.details["category_id"] = category_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении категории по ID: {str(e)}",
                details={"use_case": "GetCategoryUseCase", "category_id": category_id}
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> CategoryListResponse:
        try:
            with self._database.session() as session:
                categories, total = self._repo.get_all(session, skip, limit)
                return CategoryListResponse(
                    items=[CategoryResponse.model_validate(c) for c in categories],
                    total=total
                )

        except DatabaseException as e:
            e.details["use_case"] = "GetCategoryUseCase"
            e.details["method"] = "get_all"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка категорий: {str(e)}",
                details={"use_case": "GetCategoryUseCase"}
            )

    async def get_by_slug(self, slug: str) -> CategoryResponse:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_slug(session, slug)
                if not category:
                    raise NotFoundException(
                        resource="Category",
                        field="slug",
                        value=slug
                    )
                return CategoryResponse.model_validate(category)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetCategoryUseCase"
            e.details["method"] = "get_by_slug"
            e.details["slug"] = slug
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении категории по slug: {str(e)}",
                details={"use_case": "GetCategoryUseCase", "slug": slug}
            )