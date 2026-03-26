from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.locations import LocationResponse, LocationListResponse
from src.exceptions import NotFoundException, DatabaseException

class GetLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def get_by_id(self, location_id: int) -> LocationResponse:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_id(session, location_id)
                if not location:
                    raise NotFoundException(
                        resource="Location",
                        field="id",
                        value=location_id
                    )
                return LocationResponse.model_validate(location)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetLocationUseCase"
            e.details["method"] = "get_by_id"
            e.details["location_id"] = location_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении локации по ID: {str(e)}",
                details={"use_case": "GetLocationUseCase", "location_id": location_id}
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> LocationListResponse:
        try:
            with self._database.session() as session:
                locations, total = self._repo.get_all(session, skip, limit)
                return LocationListResponse(
                    items=[LocationResponse.model_validate(l) for l in locations],
                    total=total
                )

        except DatabaseException as e:
            e.details["use_case"] = "GetLocationUseCase"
            e.details["method"] = "get_all"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка локаций: {str(e)}",
                details={"use_case": "GetLocationUseCase"}
            )

    async def get_by_name(self, name: str) -> LocationResponse:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_name(session, name)
                if not location:
                    raise NotFoundException(
                        resource="Location",
                        field="name",
                        value=name
                    )
                return LocationResponse.model_validate(location)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetLocationUseCase"
            e.details["method"] = "get_by_name"
            e.details["name"] = name
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении локации по имени: {str(e)}",
                details={"use_case": "GetLocationUseCase", "name": name}
            )