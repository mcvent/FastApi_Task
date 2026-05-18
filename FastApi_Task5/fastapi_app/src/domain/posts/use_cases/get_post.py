from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.schemas.posts import PostResponse, PostListResponse
from src.exceptions import NotFoundException, DatabaseException
import logging

logger = logging.getLogger(__name__)


class GetPostUseCase:
    def __init__(self, repo: PostRepository):
        self._repo = repo

    async def get_by_id(self, session: AsyncSession, post_id: int) -> PostResponse:
        try:
            post = await self._repo.get_by_id(session, post_id)
            if not post:
                raise NotFoundException(
                    resource="Post",
                    field="id",
                    value=post_id
                )
            return PostResponse.model_validate(post)
        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetPostUseCase"
            e.details["method"] = "get_by_id"
            e.details["post_id"] = post_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении поста по ID: {str(e)}",
                details={"use_case": "GetPostUseCase", "post_id": post_id}
            )

    async def get_all(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> PostListResponse:
        try:
            posts, total = await self._repo.get_all(session, skip, limit)
            return PostListResponse(
                items=[PostResponse.model_validate(p) for p in posts],
                total=total
            )
        except DatabaseException as e:
            e.details["use_case"] = "GetPostUseCase"
            e.details["method"] = "get_all"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка постов: {str(e)}",
                details={"use_case": "GetPostUseCase"}
            )

    async def get_by_author(self, session: AsyncSession, author_id: int, skip: int = 0, limit: int = 100) -> PostListResponse:
        try:
            posts, total = await self._repo.get_by_author(session, author_id, skip, limit)
            return PostListResponse(
                items=[PostResponse.model_validate(p) for p in posts],
                total=total
            )
        except DatabaseException as e:
            e.details["use_case"] = "GetPostUseCase"
            e.details["method"] = "get_by_author"
            e.details["author_id"] = author_id
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении постов автора: {str(e)}",
                details={"use_case": "GetPostUseCase", "author_id": author_id}
            )

    async def get_published(self, session: AsyncSession, skip: int = 0, limit: int = 100) -> PostListResponse:
        try:
            posts, total = await self._repo.get_published(session, skip, limit)
            return PostListResponse(
                items=[PostResponse.model_validate(p) for p in posts],
                total=total
            )
        except DatabaseException as e:
            e.details["use_case"] = "GetPostUseCase"
            e.details["method"] = "get_published"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении опубликованных постов: {str(e)}",
                details={"use_case": "GetPostUseCase"}
            )