from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.schemas.locations import LocationCreate, LocationResponse
from src.exceptions import ConflictError, DatabaseException, ForbiddenError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CreateLocationUseCase:
    def __init__(self, session: AsyncSession, repo: LocationRepository):
        self._session = session
        self._repo = repo

    async def execute(self, location_data: LocationCreate, current_user: dict) -> LocationResponse:
        try:
            if not current_user.get("is_superuser"):
                raise ForbiddenError(
                    message="Только суперпользователи могут создавать локации",
                    required_role="superuser",
                    user_role="user" if not current_user.get("is_superuser") else "superuser"
                )

            # Проверка на дубликат имени
            if await self._repo.name_exists(self._session, location_data.name):
                raise ConflictError(
                    resource="Location",
                    field="name",
                    value=location_data.name
                )

            location_dict = location_data.model_dump()
            location_dict["created_at"] = datetime.now()

            location = await self._repo.create(self._session, location_dict)
            await self._session.commit()

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