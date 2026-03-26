from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.schemas.comments import CommentResponse, CommentListResponse
from src.exceptions import NotFoundException, DatabaseException

class GetCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()

    async def get_by_id(self, comment_id: int) -> CommentResponse:
        try:
            with self._database.session() as session:
                comment = self._repo.get_by_id(session, comment_id)
                if not comment:
                    raise NotFoundException(
                        resource="Comment",
                        field="id",
                        value=comment_id
                    )
                return CommentResponse.model_validate(comment)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetCommentUseCase"
            e.details["method"] = "get_by_id"
            e.details["comment_id"] = comment_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении комментария по ID: {str(e)}",
                details={"use_case": "GetCommentUseCase", "comment_id": comment_id}
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> CommentListResponse:
        try:
            with self._database.session() as session:
                comments, total = self._repo.get_all(session, skip, limit)
                return CommentListResponse(
                    items=[CommentResponse.model_validate(c) for c in comments],
                    total=total
                )

        except DatabaseException as e:
            e.details["use_case"] = "GetCommentUseCase"
            e.details["method"] = "get_all"
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка комментариев: {str(e)}",
                details={"use_case": "GetCommentUseCase"}
            )

    async def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> CommentListResponse:
        try:
            with self._database.session() as session:
                comments, total = self._repo.get_by_post(session, post_id, skip, limit)
                return CommentListResponse(
                    items=[CommentResponse.model_validate(c) for c in comments],
                    total=total
                )

        except DatabaseException as e:
            e.details["use_case"] = "GetCommentUseCase"
            e.details["method"] = "get_by_post"
            e.details["post_id"] = post_id
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении комментариев поста: {str(e)}",
                details={"use_case": "GetCommentUseCase", "post_id": post_id}
            )

    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> CommentListResponse:
        try:
            with self._database.session() as session:
                comments, total = self._repo.get_by_author(session, author_id, skip, limit)
                return CommentListResponse(
                    items=[CommentResponse.model_validate(c) for c in comments],
                    total=total
                )

        except DatabaseException as e:
            e.details["use_case"] = "GetCommentUseCase"
            e.details["method"] = "get_by_author"
            e.details["author_id"] = author_id
            e.details["skip"] = skip
            e.details["limit"] = limit
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении комментариев автора: {str(e)}",
                details={"use_case": "GetCommentUseCase", "author_id": author_id}
            )