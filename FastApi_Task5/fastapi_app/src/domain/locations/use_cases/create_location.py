from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.schemas.locations import LocationCreate, LocationResponse
from src.exceptions import ConflictError, DatabaseException, ForbiddenError
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class CreateLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_data: LocationCreate,  current_user: dict) -> LocationResponse:
        try:
            if not current_user.get("is_superuser"):
                raise ForbiddenError(
                    message="Только суперпользователи могут создавать категории",
                    required_role="superuser",
                    user_role="user" if not current_user.get("is_superuser") else "superuser"
                )
            async with self._database.session() as session:
                # Проверка на дубликат имени
                if await self._repo.name_exists(session, location_data.name):
                    raise ConflictError(
                        resource="Location",
                        field="name",
                        value=location_data.name
                    )

                location_dict = location_data.model_dump()
                location_dict["created_at"] = datetime.now()

                location = await self._repo.create(session, location_dict)
                await session.commit()

                return LocationResponse.model_validate(location)

        except (ConflictError, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreateLocationUseCase"
            e.details["name"] = location_data.name
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при создании локации: {str(e)}",
                details={"use_case": "CreateLocationUseCase", "name": location_data.name}
            )