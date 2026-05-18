from fastapi import APIRouter, Query, status, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.posts import PostCreate, PostUpdate, PostResponse, PostListResponse, PostImageResponse
from src.domain.posts.use_cases.create_post import CreatePostUseCase
from src.domain.posts.use_cases.get_post import GetPostUseCase
from src.domain.posts.use_cases.update_post import UpdatePostUseCase
from src.domain.posts.use_cases.delete_post import DeletePostUseCase
from src.domain.posts.use_cases.add_post_image import AddPostImageUseCase
from src.schemas.posts import PostImagesListResponse
from src.domain.posts.use_cases.get_post_image import GetPostImageUseCase
from src.domain.posts.use_cases.delete_post_image import DeletePostImageUseCase
from src.core.dependencies import get_current_user
from src.exceptions import AppException
from src.infrastructure.postgres.database import database

from typing import Annotated
from dishka.integrations.fastapi import FromDishka, inject
from fastapi.responses import FileResponse
import logging

logger = logging.getLogger(__name__)

public_router = APIRouter(prefix="/posts", tags=["Posts"])
protected_router = APIRouter(prefix="/posts", tags=["Posts"], dependencies=[Depends(get_current_user)])


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
        "comment_not_found": status.HTTP_404_NOT_FOUND,
        "post_not_found": status.HTTP_404_NOT_FOUND,
        "image_not_found": status.HTTP_404_NOT_FOUND,
        "post_has_no_image": status.HTTP_404_NOT_FOUND,
        "upload_file_is_not_image": status.HTTP_400_BAD_REQUEST,
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


# ==================== PUBLIC GET ====================

@public_router.get("/", response_model=PostListResponse)
@inject
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    use_case: FromDishka[GetPostUseCase] = None,
):
    try:
        async with database.session() as session:
            return await use_case.get_all(session, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/{post_id}", response_model=PostResponse)
@inject
async def get_post(
    post_id: int,
    use_case: FromDishka[GetPostUseCase] = None,
):
    try:
        async with database.session() as session:
            return await use_case.get_by_id(session, post_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/author/{author_id}", response_model=PostListResponse)
@inject
async def get_posts_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    use_case: FromDishka[GetPostUseCase] = None,
):
    try:
        async with database.session() as session:
            return await use_case.get_by_author(session, author_id, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/published/", response_model=PostListResponse)
@inject
async def get_published_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    use_case: FromDishka[GetPostUseCase] = None,
):
    try:
        async with database.session() as session:
            return await use_case.get_published(session, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/{post_id}/images/", response_model=PostImagesListResponse)
@inject
async def get_post_images(
    post_id: int,
    use_case: FromDishka[GetPostImageUseCase] = None,
):
    try:
        async with database.session() as session:
            return await use_case.get_all_images(session, post_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/{post_id}/images/{image_id}/", response_class=FileResponse)
@inject
async def get_post_image_by_id(
    post_id: int,
    image_id: int,
    use_case: FromDishka[GetPostImageUseCase] = None,
):
    try:
        async with database.session() as session:
            return await use_case.get_image_by_id(session, post_id, image_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


# ==================== PROTECTED POST/PATCH/DELETE ====================

@protected_router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
@inject
async def create_post(
    post_data: PostCreate,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[CreatePostUseCase] = None,
) -> PostResponse:
    try:
        return await use_case.execute(post_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.patch("/{post_id}", response_model=PostResponse)
@inject
async def update_post(
    post_id: int,
    update_data: PostUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[UpdatePostUseCase] = None,
) -> PostResponse:
    try:
        return await use_case.execute(post_id, update_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.delete("/{post_id}", status_code=204)
@inject
async def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[DeletePostUseCase] = None,
):
    try:
        await use_case.execute(post_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.post("/{post_id}/images/", status_code=status.HTTP_201_CREATED, response_model=PostImageResponse)
@inject
async def add_post_image(
    post_id: int,
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[AddPostImageUseCase] = None,
):
    try:
        return await use_case.execute(post_id, image, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.delete("/{post_id}/images/{image_id}/", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_post_image(
    post_id: int,
    image_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[DeletePostImageUseCase] = None,
):
    try:
        await use_case.execute(post_id, image_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)