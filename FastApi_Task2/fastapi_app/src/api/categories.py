from fastapi import APIRouter, Query
from src.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse
from src.domain.categories.use_cases.create_category import CreateCategoryUseCase
from src.domain.categories.use_cases.get_category import GetCategoryUseCase
from src.domain.categories.use_cases.update_category import UpdateCategoryUseCase
from src.domain.categories.use_cases.delete_category import DeleteCategoryUseCase

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", status_code=201, response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate):
    use_case = CreateCategoryUseCase()
    return await use_case.execute(category_data)


@router.get("/", response_model=CategoryListResponse)
async def get_all_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetCategoryUseCase()
    return await use_case.get_all(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int):
    use_case = GetCategoryUseCase()
    return await use_case.get_by_id(category_id)


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(slug: str):
    use_case = GetCategoryUseCase()
    return await use_case.get_by_slug(slug)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, update_data: CategoryUpdate):
    use_case = UpdateCategoryUseCase()
    return await use_case.execute(category_id, update_data)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int):
    use_case = DeleteCategoryUseCase()
    await use_case.execute(category_id)