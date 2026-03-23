from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from fastapi import HTTPException, status


class DeleteLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_id: int) -> bool:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_id(session, location_id)
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Локация не найдена"
                    )

                success = self._repo.delete(session, location_id)
                session.commit()
                return success

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при удалении локации: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )