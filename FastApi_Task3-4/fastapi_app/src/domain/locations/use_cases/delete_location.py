from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.exceptions import NotFoundException, DatabaseException

class DeleteLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_id: int) -> bool:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_id(session, location_id)
                if not location:
                    raise NotFoundException(
                        resource="Location",
                        field="id",
                        value=location_id
                    )

                success = self._repo.delete(session, location_id)
                session.commit()
                return success

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteLocationUseCase"
            e.details["location_id"] = location_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении локации: {str(e)}",
                details={"use_case": "DeleteLocationUseCase", "location_id": location_id}
            )