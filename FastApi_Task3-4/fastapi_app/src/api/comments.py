from fastapi import APIRouter, Query
from src.schemas.comments import CommentCreate, CommentUpdate, CommentResponse, CommentListResponse
from src.domain.comments.use_cases.create_comment import CreateCommentUseCase
from src.domain.comments.use_cases.get_comment import GetCommentUseCase
from src.domain.comments.use_cases.update_comment import UpdateCommentUseCase
from src.domain.comments.use_cases.delete_comment import DeleteCommentUseCase

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post("/", status_code=201, response_model=CommentResponse)
async def create_comment(comment_data: CommentCreate):
    use_case = CreateCommentUseCase()
    return await use_case.execute(comment_data)


@router.get("/", response_model=CommentListResponse)
async def get_all_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetCommentUseCase()
    return await use_case.get_all(skip=skip, limit=limit)


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(comment_id: int):
    use_case = GetCommentUseCase()
    return await use_case.get_by_id(comment_id)


@router.get("/post/{post_id}", response_model=CommentListResponse)
async def get_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetCommentUseCase()
    return await use_case.get_by_post(post_id, skip=skip, limit=limit)


@router.get("/author/{author_id}", response_model=CommentListResponse)
async def get_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetCommentUseCase()
    return await use_case.get_by_author(author_id, skip=skip, limit=limit)


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: int, update_data: CommentUpdate):
    use_case = UpdateCommentUseCase()
    return await use_case.execute(comment_id, update_data)


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: int):
    use_case = DeleteCommentUseCase()
    await use_case.execute(comment_id)
