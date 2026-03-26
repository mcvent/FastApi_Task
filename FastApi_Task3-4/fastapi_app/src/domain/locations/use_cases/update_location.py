from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.locations import LocationUpdate, LocationResponse
from src.exceptions import NotFoundException, ConflictError, DatabaseException

class UpdateLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_id: int, update_data: LocationUpdate) -> LocationResponse:
        try:
            with self._database.session() as session:
                # Проверяем существование локации
                existing_location = self._repo.get_by_id(session, location_id)
                if not existing_location:
                    raise NotFoundException(
                        resource="Location",
                        field="id",
                        value=location_id
                    )

                # Если меняется имя, проверяем на дубликат
                if update_data.name is not None and update_data.name != existing_location.name:
                    if self._repo.name_exists(session, update_data.name):
                        raise ConflictError(
                            resource="Location",
                            field="name",
                            value=update_data.name
                        )

                location = self._repo.update(
                    session,
                    location_id,
                    update_data.model_dump(exclude_unset=True)
                )
                session.commit()

                return LocationResponse.model_validate(location)

        except (NotFoundException, ConflictError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "UpdateLocationUseCase"
            e.details["location_id"] = location_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при обновлении локации: {str(e)}",
                details={"use_case": "UpdateLocationUseCase", "location_id": location_id}
            )