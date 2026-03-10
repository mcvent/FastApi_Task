from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.locations import LocationCreate, LocationResponse
from fastapi import HTTPException, status
from datetime import datetime


class CreateLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def execute(self, location_: LocationCreate

    ) -> LocationResponse:
        try:
            with self._database.session() as session:
                if self._repo.name_exists(session, location_.name):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Локация с именем '{location_.name}' уже существует"
                    )

                location_dict = location_.model_dump()
                location_dict["created_at"] = datetime.now()

                location = self._repo.create(session, location_dict)
                session.commit()

                return LocationResponse.model_validate(location)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при создании локации: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )