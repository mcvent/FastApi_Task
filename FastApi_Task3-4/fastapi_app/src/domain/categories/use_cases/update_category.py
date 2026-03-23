from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryUpdate, CategoryResponse
from fastapi import HTTPException, status


class UpdateCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_id: int, update_data: CategoryUpdate) -> CategoryResponse:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_id(session, category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Категория не найдена"
                    )

                if update_data.slug:
                    if self._repo.slug_exists(session, update_data.slug):
                        existing = self._repo.get_by_slug(session, update_data.slug)
                        if existing and existing.id != category_id:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Категория с slug '{update_data.slug}' уже существует"
                            )

                category = self._repo.update(session, category_id, update_data.model_dump(exclude_unset=True))
                session.commit()

                return CategoryResponse.model_validate(category)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при обновлении категории: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )