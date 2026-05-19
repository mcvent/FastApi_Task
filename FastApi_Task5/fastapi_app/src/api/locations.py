from fastapi import APIRouter, Query, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.locations import LocationCreate, LocationUpdate, LocationResponse, LocationListResponse
from src.domain.locations.use_cases.create_location import CreateLocationUseCase
from src.domain.locations.use_cases.get_location import GetLocationUseCase
from src.domain.locations.use_cases.update_location import UpdateLocationUseCase
from src.domain.locations.use_cases.delete_location import DeleteLocationUseCase
from src.core.dependencies import get_current_user
from src.exceptions import AppException
from src.infrastructure.postgres.database import database

from dishka.integrations.fastapi import FromDishka, inject
import logging

logger = logging.getLogger(__name__)

# Публичный роутер - для GET запросов (без авторизации)
public_router = APIRouter(prefix="/locations", tags=["Locations"])

# Защищенный роутер - для POST, PATCH, DELETE (с авторизацией)
protected_router = APIRouter(prefix="/locations", tags=["Locations"], dependencies=[Depends(get_current_user)])


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
        "forbidden": status.HTTP_403_FORBIDDEN,
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


# ==================== PUBLIC ROUTES ====================

@public_router.get("/", response_model=LocationListResponse)
@inject
async def get_all_locations(
    skip: int = Query(0, ge=0),
    session: FromDishka[AsyncSession] = None,
    limit: int = Query(100, ge=1, le=1000),
    use_case: FromDishka[GetLocationUseCase] = None,
):
    try:
        return await use_case.get_all(session, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/{location_id}", response_model=LocationResponse)
@inject
async def get_location(
    location_id: int,
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetLocationUseCase] = None,
):
    try:
        return await use_case.get_by_id(session, location_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/name/{name}", response_model=LocationResponse)
@inject
async def get_location_by_name(
    name: str,
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetLocationUseCase] = None,
):
    try:
        return await use_case.get_by_name(session, name)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


# ==================== PROTECTED ROUTES ====================

@protected_router.post("/", status_code=201, response_model=LocationResponse)
@inject
async def create_location(
    location_data: LocationCreate,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[CreateLocationUseCase] = None,
):
    try:
        return await use_case.execute(location_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.patch("/{location_id}", response_model=LocationResponse)
@inject
async def update_location(
    location_id: int,
    update_data: LocationUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[UpdateLocationUseCase] = None,
):
    try:
        return await use_case.execute(location_id, update_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.delete("/{location_id}", status_code=204)
@inject
async def delete_location(
    location_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[DeleteLocationUseCase] = None,
):
    try:
        await use_case.execute(location_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)