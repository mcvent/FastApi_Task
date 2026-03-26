from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from src.schemas.locations import LocationCreate, LocationUpdate, LocationResponse, LocationListResponse
from src.domain.locations.use_cases.create_location import CreateLocationUseCase
from src.domain.locations.use_cases.get_location import GetLocationUseCase
from src.domain.locations.use_cases.update_location import UpdateLocationUseCase
from src.domain.locations.use_cases.delete_location import DeleteLocationUseCase
from src.exceptions import AppException

router = APIRouter(prefix="/locations", tags=["Locations"])

def handle_app_exception(exc: AppException) -> JSONResponse:
    """Конвертация AppException в HTTPException"""
    status_code_map = {
        "not_found": status.HTTP_404_NOT_FOUND,
        "conflict": status.HTTP_409_CONFLICT,
        "validation_error": status.HTTP_400_BAD_REQUEST,
        "unprocessable": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "database_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "db_connection_error": status.HTTP_503_SERVICE_UNAVAILABLE,
        "db_query_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "db_integrity_error": status.HTTP_400_BAD_REQUEST,
    }
    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@router.post("/", status_code=201, response_model=LocationResponse)
async def create_location(location_data: LocationCreate):
    try:
        use_case = CreateLocationUseCase()
        return await use_case.execute(location_data)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/", response_model=LocationListResponse)
async def get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetLocationUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/{location_id}", response_model=LocationResponse)
async def get_location(location_id: int):
    try:
        use_case = GetLocationUseCase()
        return await use_case.get_by_id(location_id)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/name/{name}", response_model=LocationResponse)
async def get_location_by_name(name: str):
    try:
        use_case = GetLocationUseCase()
        return await use_case.get_by_name(name)
    except AppException as e:
        return handle_app_exception(e)

@router.patch("/{location_id}", response_model=LocationResponse)
async def update_location(location_id: int, update_data: LocationUpdate):
    try:
        use_case = UpdateLocationUseCase()
        return await use_case.execute(location_id, update_data)
    except AppException as e:
        return handle_app_exception(e)

@router.delete("/{location_id}", status_code=204)
async def delete_location(location_id: int):
    try:
        use_case = DeleteLocationUseCase()
        await use_case.execute(location_id)
    except AppException as e:
        return handle_app_exception(e)