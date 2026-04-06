from fastapi import APIRouter, Query, status, Depends
from fastapi.responses import JSONResponse
from src.schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
from src.domain.users.use_cases.create_user import CreateUserUseCase
from src.domain.users.use_cases.get_user import GetUserUseCase
from src.domain.users.use_cases.update_user import UpdateUserUseCase
from src.domain.users.use_cases.delete_user import DeleteUserUseCase
from src.core.dependencies import get_current_user
from src.exceptions import AppException

# Публичный роутер - для GET и POST (регистрация) без авторизации
public_router = APIRouter(prefix="/users", tags=["Users"])

# Защищенный роутер - для PATCH, DELETE (требуют авторизацию)
protected_router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(get_current_user)])


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


# --- PUBLIC ROUTES (GET и create) на public_router ---

@public_router.post("/create", status_code=201, response_model=UserResponse)
async def create_user(user_data: UserCreate):
    """Регистрация нового пользователя (публичный эндпоинт)"""
    try:
        use_case = CreateUserUseCase()
        return await use_case.execute(user_data, is_public=True)
    except AppException as e:
        return handle_app_exception(e)


@public_router.get("/", response_model=UserListResponse)
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetUserUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)


@public_router.get("/active", response_model=UserListResponse)
async def get_active_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetUserUseCase()
        return await use_case.get_active_users(skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)


@public_router.get("/id/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    try:
        use_case = GetUserUseCase()
        return await use_case.get_by_id(user_id)
    except AppException as e:
        return handle_app_exception(e)


@public_router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    try:
        use_case = GetUserUseCase()
        return await use_case.get_by_username(username)
    except AppException as e:
        return handle_app_exception(e)


@public_router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    try:
        use_case = GetUserUseCase()
        return await use_case.get_by_email(email)
    except AppException as e:
        return handle_app_exception(e)


# --- PROTECTED ROUTES (PATCH, DELETE) на protected_router ---

@protected_router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Обновление пользователя - только сам пользователь"""
    try:
        use_case = UpdateUserUseCase()
        return await use_case.execute(user_id, update_data, current_user)
    except AppException as e:
        return handle_app_exception(e)


@protected_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Удаление пользователя - сам пользователь или админ"""
    try:
        use_case = DeleteUserUseCase()
        await use_case.execute(user_id, current_user)
    except AppException as e:
        return handle_app_exception(e)