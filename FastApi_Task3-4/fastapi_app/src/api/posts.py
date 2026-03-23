from fastapi import APIRouter, Query
from src.schemas.posts import PostCreate, PostUpdate, PostResponse, PostListResponse
from src.domain.posts.use_cases.create_post import CreatePostUseCase
from src.domain.posts.use_cases.get_post import GetPostUseCase
from src.domain.posts.use_cases.update_post import UpdatePostUseCase
from src.domain.posts.use_cases.delete_post import DeletePostUseCase

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", status_code=201, response_model=PostResponse)
async def create_post(post_: PostCreate):
    use_case = CreatePostUseCase()
    return await use_case.execute(post_)


@router.get("/", response_model=PostListResponse)
async def get_all_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetPostUseCase()
    return await use_case.get_all(skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    use_case = GetPostUseCase()
    return await use_case.get_by_id(post_id)


@router.get("/author/{author_id}", response_model=PostListResponse)
async def get_posts_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetPostUseCase()
    return await use_case.get_by_author(author_id, skip=skip, limit=limit)


@router.get("/published/", response_model=PostListResponse)
async def get_published_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    use_case = GetPostUseCase()
    return await use_case.get_published(skip=skip, limit=limit)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, update_data: PostUpdate):
    use_case = UpdatePostUseCase()
    return await use_case.execute(post_id, update_data)


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int):
    use_case = DeletePostUseCase()
    await use_case.execute(post_id)