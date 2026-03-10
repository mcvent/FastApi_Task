from fastapi import APIRouter, Depends, Query
from src.schemas.users import UserCreate, UserUpdate, UserResponse, UserListResponse
from src.domain.users.use_cases.create_user import CreateUserUseCase
from src.domain.users.use_cases.get_user import GetUserUseCase
from src.domain.users.use_cases.update_user import UpdateUserUseCase
from src.domain.users.use_cases.delete_user import DeleteUserUseCase

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=201, response_model=UserResponse)
async def create_user(user: UserCreate):
    use_case = CreateUserUseCase()
    return await use_case.execute(user)


@router.get("/", response_model=UserListResponse)
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetUserUseCase()
    return await use_case.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    use_case = GetUserUseCase()
    return await use_case.get_by_id(user_id)


@router.get("/username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str):
    use_case = GetUserUseCase()
    return await use_case.get_by_username(username)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, update_data: UserUpdate):
    use_case = UpdateUserUseCase()
    return await use_case.execute(user_id, update_data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int):
    use_case = DeleteUserUseCase()
    await use_case.execute(user_id)