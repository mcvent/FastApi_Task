from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging
logger = logging.getLogger(__name__)

class DeleteLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_id: int,  current_user: dict) -> bool:
        try:
            if not current_user.get("is_superuser"):
                raise ForbiddenError(
                    message="Только суперпользователи могут создавать категории",
                    required_role="superuser",
                    user_role="user" if not current_user.get("is_superuser") else "superuser"
                )
            async with self._database.session() as session:
                location = await self._repo.get_by_id(session, location_id)
                if not location:
                    raise NotFoundException(
                        resource="Location",
                        field="id",
                        value=location_id
                    )

                success = await self._repo.delete(session, location_id)
                await session.commit()
                return success

        except (NotFoundException, ForbiddenError):
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