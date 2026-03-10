from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryResponse, CategoryListResponse
from fastapi import HTTPException, status


class GetCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def get_by_id(self, category_id: int) -> CategoryResponse:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_id(session, category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Категория не найдена"
                    )
                return CategoryResponse.model_validate(category)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении категории по ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> CategoryListResponse:
        try:
            with self._database.session() as session:
                categories, total = self._repo.get_all(session, skip, limit)
                return CategoryListResponse(
                    items=[CategoryResponse.model_validate(c) for c in categories],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении списка категорий: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_by_slug(self, slug: str) -> CategoryResponse:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_slug(session, slug)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Категория не найдена"
                    )
                return CategoryResponse.model_validate(category)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении категории по slug: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )