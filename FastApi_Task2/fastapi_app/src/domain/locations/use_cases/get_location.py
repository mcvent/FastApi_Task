from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.locations import LocationResponse, LocationListResponse
from fastapi import HTTPException, status


class GetLocationUseCase:
    def __init__(self):
        self._database = database
        self._repo = LocationRepository()

    async def get_by_id(self, location_id: int) -> LocationResponse:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_id(session, location_id)
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Локация не найдена"
                    )
                return LocationResponse.model_validate(location)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении локации по ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> LocationListResponse:
        try:
            with self._database.session() as session:
                locations, total = self._repo.get_all(session, skip, limit)
                return LocationListResponse(
                    items=[LocationResponse.model_validate(l) for l in locations],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении списка локаций: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_by_name(self, name: str) -> LocationResponse:
        try:
            with self._database.session() as session:
                location = self._repo.get_by_name(session, name)
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Локация не найдена"
                    )
                return LocationResponse.model_validate(location)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении локации по имени: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )