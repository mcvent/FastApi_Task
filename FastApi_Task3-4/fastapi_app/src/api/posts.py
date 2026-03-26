from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from src.schemas.posts import PostCreate, PostUpdate, PostResponse, PostListResponse
from src.domain.posts.use_cases.create_post import CreatePostUseCase
from src.domain.posts.use_cases.get_post import GetPostUseCase
from src.domain.posts.use_cases.update_post import UpdatePostUseCase
from src.domain.posts.use_cases.delete_post import DeletePostUseCase
from src.exceptions import AppException

router = APIRouter(prefix="/posts", tags=["Posts"])

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

@router.post("/", status_code=201, response_model=PostResponse)
async def create_post(post_data: PostCreate):
    try:
        use_case = CreatePostUseCase()
        return await use_case.execute(post_data)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/", response_model=PostListResponse)
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_by_id(post_id)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/author/{author_id}", response_model=PostListResponse)
async def get_posts_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_by_author(author_id, skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/published/", response_model=PostListResponse)
async def get_published_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_published(skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, update_data: PostUpdate):
    try:
        use_case = UpdatePostUseCase()
        return await use_case.execute(post_id, update_data)
    except AppException as e:
        return handle_app_exception(e)

@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int):
    try:
        use_case = DeletePostUseCase()
        await use_case.execute(post_id)
    except AppException as e:
        return handle_app_exception(e)