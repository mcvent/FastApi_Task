from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.exceptions import NotFoundException, DatabaseException

class DeleteCategoryUseCase:
    def __init__(self):
        self._database = database
        self._repo = CategoryRepository()

    async def execute(self, category_id: int) -> bool:
        try:
            with self._database.session() as session:
                category = self._repo.get_by_id(session, category_id)
                if not category:
                    raise NotFoundException(
                        resource="Category",
                        field="id",
                        value=category_id
                    )

                success = self._repo.delete(session, category_id)
                session.commit()
                return success

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteCategoryUseCase"
            e.details["category_id"] = category_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении категории: {str(e)}",
                details={"use_case": "DeleteCategoryUseCase", "category_id": category_id}
            )