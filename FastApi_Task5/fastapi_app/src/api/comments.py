from fastapi import APIRouter, Query, status, Depends
from fastapi.responses import JSONResponse
from src.schemas.comments import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from src.domain.comments.use_cases.create_comment import CreateCommentUseCase
from src.domain.comments.use_cases.get_comment import GetCommentUseCase
from src.domain.comments.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comments.use_cases.delete_comment import DeleteCommentUseCase
from src.core.dependencies import get_current_user
from src.exceptions import AppException
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

@public_router.get("/", response_model=CommentListResponse)
async def get_all_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_by_id(comment_id)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/post/{post_id}", response_model=CommentListResponse)
async def get_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_by_post(post_id, skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@public_router.get("/author/{author_id}", response_model=CommentListResponse)
async def get_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_by_author(author_id, skip=skip, limit=limit)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

# --- PROTECTED ROUTES (POST, PATCH, DELETE) на protected_router ---

@protected_router.post("/", status_code=201, response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = CreateCommentUseCase()
        return await use_case.execute(comment_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@protected_router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    update_data: CommentUpdate,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = UpdateCommentUseCase()
        return await use_case.execute(comment_id, update_data, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)

@protected_router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        use_case = DeleteCommentUseCase()
        await use_case.execute(comment_id, current_user)
    except AppException as e:
        logger.error(e.get_detail())
        return handle_app_exception(e)