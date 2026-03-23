from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.locations import LocationUpdate, LocationResponse
from fastapi import HTTPException, status


class UpdateLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_id: int, update_data: LocationUpdate

    ) -> LocationResponse:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_id(session, location_id)
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Локация не найдена"
                    )

                if update_data.name:
                    if self._repo.name_exists(session, update_data.name):
                        existing = self._repo.get_by_name(session, update_data.name)
                        if existing and existing.id != location_id:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Локация с именем '{update_data.name}' уже существует"
                            )

                location = self._repo.update(session, location_id, update_data.model_dump(exclude_unset=True))
                session.commit()

                return LocationResponse.model_validate(location)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при обновлении локации: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )