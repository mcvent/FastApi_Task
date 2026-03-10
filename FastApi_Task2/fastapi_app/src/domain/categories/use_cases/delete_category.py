from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from fastapi import HTTPException, status


class DeleteCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_id: int) -> bool:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_id(session, category_id)
                if not category:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Категория не найдена"
                    )

                success = self._repo.delete(session, category_id)
                session.commit()
                return success

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при удалении категории: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )