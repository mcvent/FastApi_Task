from fastapi import APIRouter, Query, status, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from src.schemas.posts import PostCreate, PostUpdate, PostResponse, PostListResponse, PostImageResponse
from src.domain.posts.use_cases.create_post import CreatePostUseCase
from src.domain.posts.use_cases.get_post import GetPostUseCase
from src.domain.posts.use_cases.update_post import UpdatePostUseCase
from src.domain.posts.use_cases.delete_post import DeletePostUseCase
from src.domain.posts.use_cases.get_post_image import GetPostImageUseCase
from src.domain.posts.use_cases.add_post_image import AddPostImageUseCase
from src.core.dependencies import get_current_user
from src.exceptions import (AppException, PostNotFoundByIdException, PostHasNoImageException,
                            UploadFileIsNotImageException)

from fastapi.responses import FileResponse
import logging
logger = logging.getLogger(__name__)
# Публичный роутер - для GET запросов (без авторизации)
public_router = APIRouter(prefix="/posts", tags=["Posts"])

# Защищенный роутер - для POST, PATCH, DELETE (с авторизацией)
protected_router = APIRouter(prefix="/posts", tags=["Posts"], dependencies=[Depends(get_current_user)])

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

# --- PUBLIC ROUTES (GET) на public_router ---

@public_router.get("/", response_model=PostListResponse)
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_by_id(post_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/author/{author_id}", response_model=PostListResponse)
async def get_posts_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_by_author(author_id, skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/published/", response_model=PostListResponse)
async def get_published_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetPostUseCase()
        return await use_case.get_published(skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

# --- PROTECTED ROUTES (POST, PATCH, DELETE) на protected_router ---

@protected_router.post("/", status_code=201, response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = CreatePostUseCase()
        return await use_case.execute(post_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@protected_router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    update_data: PostUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = UpdatePostUseCase()
        return await use_case.execute(post_id, update_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@protected_router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = DeletePostUseCase()
        await use_case.execute(post_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/image/post/{post_id}", status_code=status.HTTP_200_OK, response_class=FileResponse)
async def get_post_image(
    post_id: int,
    use_case: GetPostImageUseCase = Depends()
):
    try:
        return await use_case.execute(post_id=post_id)
    except (PostNotFoundByIdException, PostHasNoImageException) as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.post("/image/post/{post_id}", status_code=status.HTTP_201_CREATED, response_model=PostImageResponse)
async def add_post_image(
    post_id: int,
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    use_case: AddPostImageUseCase = Depends()
):
    try:
        return await use_case.execute(post_id=post_id, image=image, current_user=current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)