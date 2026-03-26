from fastapi import APIRouter, Query, status
from fastapi.responses import JSONResponse
from src.schemas.comments import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from src.domain.comments.use_cases.create_comment import CreateCommentUseCase
from src.domain.comments.use_cases.get_comment import GetCommentUseCase
from src.domain.comments.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comments.use_cases.delete_comment import DeleteCommentUseCase
from src.exceptions import AppException

router = APIRouter(prefix="/comments", tags=["Comments"])

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

@router.post("/", status_code=201, response_model=CommentResponse)
async def create_comment(comment_data: CommentCreate):
    try:
        use_case = CreateCommentUseCase()
        return await use_case.execute(comment_data)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/", response_model=CommentListResponse)
async def get_all_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_all(skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_by_id(comment_id)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/post/{post_id}", response_model=CommentListResponse)
async def get_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_by_post(post_id, skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.get("/author/{author_id}", response_model=CommentListResponse)
async def get_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    try:
        use_case = GetCommentUseCase()
        return await use_case.get_by_author(author_id, skip=skip, limit=limit)
    except AppException as e:
        return handle_app_exception(e)

@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, update_data: CommentUpdate):
    try:
        use_case = UpdateCommentUseCase()
        return await use_case.execute(comment_id, update_data)
    except AppException as e:
        return handle_app_exception(e)

@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: int):
    try:
        use_case = DeleteCommentUseCase()
        await use_case.execute(comment_id)
    except AppException as e:
        return handle_app_exception(e)