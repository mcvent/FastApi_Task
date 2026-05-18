from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.schemas.locations import LocationUpdate, LocationResponse
from src.exceptions import NotFoundException, ConflictError, DatabaseException, ForbiddenError
import logging

logger = logging.getLogger(__name__)


class UpdateLocationUseCase:
    def __init__(self, session: AsyncSession, repo: LocationRepository):
        self._session = session
        self._repo = repo

    async def execute(self, location_id: int, update_data: LocationUpdate, current_user: dict) -> LocationResponse:
        try:
            if not current_user.get("is_superuser"):
                raise ForbiddenError(
                    message="Только суперпользователи могут обновлять локации",
                    required_role="superuser",
                    user_role="user" if not current_user.get("is_superuser") else "superuser"
                )

            # Проверяем существование локации
            existing_location = await self._repo.get_by_id(self._session, location_id)
            if not existing_location:
                raise NotFoundException(
                    resource="Location",
                    field="id",
                    value=location_id
                )

            # Если меняется имя, проверяем на дубликат
            if update_data.name is not None and update_data.name != existing_location.name:
                if await self._repo.name_exists(self._session, update_data.name):
                    raise ConflictError(
                        resource="Location",
                        field="name",
                        value=update_data.name
                    )

            location = await self._repo.update(
                self._session,
                location_id,
                update_data.model_dump(exclude_unset=True)
            )
            await self._session.commit()

            return LocationResponse.model_validate(location)

        except (NotFoundException, ConflictError, ForbiddenError):
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