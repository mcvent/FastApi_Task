from fastapi import APIRouter, Query, status, Depends
from fastapi.responses import JSONResponse
from src.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from src.domain.categories.use_cases.create_category import CreateCategoryUseCase
from src.domain.categories.use_cases.get_category import GetCategoryUseCase
from src.domain.categories.use_cases.update_category import UpdateCategoryUseCase
from src.domain.categories.use_cases.delete_category import DeleteCategoryUseCase
from src.core.dependencies import get_current_user
from src.exceptions import AppException
import logging
logger = logging.getLogger(__name__)
# Публичный роутер - для GET запросов (без авторизации)
public_router = APIRouter(prefix="/categories", tags=["Categories"])

# Защищенный роутер - для POST, PATCH, DELETE (с авторизацией)
protected_router = APIRouter(prefix="/categories", tags=["Categories"], dependencies=[Depends(get_current_user)],)

def handle_app_exception(exc: AppException) -> JSONResponse:
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

# --- PUBLIC ROUTES (GET) на public_router ---

@public_router.get("/", response_model=CategoryListResponse)
async def get_all_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCategoryUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    try:
        use_case = GetCategoryUseCase()
        return await use_case.get_by_id(category_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(slug: str):
    try:
        use_case = GetCategoryUseCase()
        return await use_case.get_by_slug(slug)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

# --- PROTECTED ROUTES (POST, PATCH, DELETE) на protected_router ---

@protected_router.post("/", status_code=201, response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = CreateCategoryUseCase()
        return await use_case.execute(category_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@protected_router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    update_data: CategoryUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = UpdateCategoryUseCase()
        return await use_case.execute(category_id, update_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@protected_router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = DeleteCategoryUseCase()
        await use_case.execute(category_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)