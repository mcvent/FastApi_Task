from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.schemas.posts import PostResponse, PostListResponse
from fastapi import HTTPException, status


class GetPostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()

    async def get_by_id(self, post_id: int) -> PostResponse:
        try:
            with self._database.session() as session:
                post = self._repo.get_by_id(session, post_id)
                if not post:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Пост с ID {post_id} не найден"
                    )
                return PostResponse.model_validate(post)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении поста по ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> PostListResponse:
        try:
            with self._database.session() as session:
                posts, total = self._repo.get_all(session, skip, limit)
                return PostListResponse(
                    items=[PostResponse.model_validate(p) for p in posts],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении списка постов: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> PostListResponse:
        try:
            with self._database.session() as session:
                posts, total = self._repo.get_by_author(session, author_id, skip, limit)
                return PostListResponse(
                    items=[PostResponse.model_validate(p) for p in posts],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении постов автора: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_published(self, skip: int = 0, limit: int = 100) -> PostListResponse:
        try:
            with self._database.session() as session:
                posts, total = self._repo.get_published(session, skip, limit)
                return PostListResponse(
                    items=[PostResponse.model_validate(p) for p in posts],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении опубликованных постов: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )