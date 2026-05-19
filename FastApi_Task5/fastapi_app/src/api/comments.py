from fastapi import APIRouter, Query, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.comments import (CommentCreate, CommentUpdate,
                                  CommentResponse, CommentListResponse,
                                  CommentImageResponse,
                                  CommentImagesListResponse
                                  )
from src.domain.comments.use_cases.create_comment import CreateCommentUseCase
from src.domain.comments.use_cases.get_comment import GetCommentUseCase
from src.domain.comments.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comments.use_cases.delete_comment import DeleteCommentUseCase
from src.domain.comments.use_cases.add_comment_image import AddCommentImageUseCase
from src.domain.comments.use_cases.get_comment_images import GetCommentImagesUseCase
from src.domain.comments.use_cases.delete_comment_image import DeleteCommentImageUseCase
from src.core.dependencies import get_current_user
from src.exceptions import AppException
from src.infrastructure.postgres.database import database

from dishka.integrations.fastapi import FromDishka, inject
import logging

logger = logging.getLogger(__name__)

# Публичный роутер - для GET запросов (без авторизации)
public_router = APIRouter(prefix="/comments", tags=["Comments"])

# Защищенный роутер - для POST, PATCH, DELETE (с авторизацией)
protected_router = APIRouter(prefix="/comments", tags=["Comments"], dependencies=[Depends(get_current_user)])


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


# ==================== PUBLIC GET ROUTES ====================

@public_router.get("/", response_model=CommentListResponse)
@inject
async def get_all_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetCommentUseCase] = None,
):
    try:
        return await use_case.get_all(session, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/{comment_id}", response_model=CommentResponse)
@inject
async def get_comment(
    comment_id: int,
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetCommentUseCase] = None,
):
    try:
        return await use_case.get_by_id(session, comment_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/post/{post_id}", response_model=CommentListResponse)
@inject
async def get_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetCommentUseCase] = None,
):
    try:
        return await use_case.get_by_post(session, post_id, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/author/{author_id}", response_model=CommentListResponse)
@inject
async def get_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetCommentUseCase] = None,
):
    try:
        return await use_case.get_by_author(session, author_id, skip, limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@public_router.get("/{comment_id}/images/", response_model=CommentImagesListResponse)
@inject
async def get_comment_images(
    comment_id: int,
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetCommentImagesUseCase] = None,
):
    try:
        return await use_case.execute(session, comment_id)
    except AppException as e:
        return handle_app_exception(e)


@public_router.get("/{comment_id}/images/{image_id}/", response_class=FileResponse)
@inject
async def get_comment_image_by_id(
    comment_id: int,
    image_id: int,
    session: FromDishka[AsyncSession] = None,
    use_case: FromDishka[GetCommentImagesUseCase] = None,
):
    try:
        return await use_case.get_by_id(session, comment_id, image_id)
    except AppException as e:
        return handle_app_exception(e)


# ==================== PROTECTED ROUTES ====================

@protected_router.post("/", status_code=201, response_model=CommentResponse)
@inject
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[CreateCommentUseCase] = None,
):
    try:
        return await use_case.execute(comment_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.patch("/{comment_id}", response_model=CommentResponse)
@inject
async def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[UpdateCommentUseCase] = None,
):
    try:
        return await use_case.execute(comment_id, update_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.delete("/{comment_id}", status_code=204)
@inject
async def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[DeleteCommentUseCase] = None,
):
    try:
        await use_case.execute(comment_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)


@protected_router.post("/{comment_id}/images/", status_code=status.HTTP_201_CREATED, response_model=CommentImageResponse)
@inject
async def add_comment_image(
    comment_id: int,
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[AddCommentImageUseCase] = None,
):
    try:
        return await use_case.execute(comment_id, image, current_user)
    except AppException as e:
        return handle_app_exception(e)


@protected_router.delete("/{comment_id}/images/{image_id}/", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_comment_image(
    comment_id: int,
    image_id: int,
    current_user: dict = Depends(get_current_user),
    use_case: FromDishka[DeleteCommentImageUseCase] = None,
):
    try:
        await use_case.execute(comment_id, image_id, current_user)
    except AppException as e:
        return handle_app_exception(e)