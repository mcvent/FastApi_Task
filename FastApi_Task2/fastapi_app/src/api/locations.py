from fastapi import APIRouter, Query
from src.schemas.locations import LocationCreate, LocationUpdate, LocationResponse, LocationListResponse
from src.domain.locations.use_cases.create_location import CreateLocationUseCase
from src.domain.locations.use_cases.get_location import GetLocationUseCase
from src.domain.locations.use_cases.update_location import UpdateLocationUseCase
from src.domain.locations.use_cases.delete_location import DeleteLocationUseCase

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", status_code=201, response_model=LocationResponse)
async def create_location(location_data: LocationCreate):
    use_case = CreateLocationUseCase()
    return await use_case.execute(location_data)


@router.get("/", response_model=LocationListResponse)
async def get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetLocationUseCase()
    return await use_case.get_all(skip=skip, limit=limit)


@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int):
    use_case = GetLocationUseCase()
    return await use_case.get_by_id(location_id)


@router.get("/name/{name}", response_model=LocationResponse)
async def get_location_by_name(name: str):
    use_case = GetLocationUseCase()
    return await use_case.get_by_name(name)


@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(location_id: int, update_: LocationUpdate):
    use_case = UpdateLocationUseCase()
    return await use_case.execute(location_id, update_)


@router.delete("/{location_id}", status_code=204)
async def delete_location(location_id: int):
    use_case = DeleteLocationUseCase()
    await use_case.execute(location_id)