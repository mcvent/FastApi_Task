from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate, CategoryResponse
from fastapi import HTTPException, status
from datetime import datetime


class CreateCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_data: CategoryCreate) -> CategoryResponse:
        try:
            with self._database.session() as session:
                if self._repo.slug_exists(session, category_data.slug):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Категория с slug '{category_data.slug}' уже существует"
                    )

                category_dict = category_data.model_dump()
                category_dict["created_at"] = datetime.now()

                category = self._repo.create(session, category_dict)
                session.commit()

                return CategoryResponse.model_validate(category)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при создании категории: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )