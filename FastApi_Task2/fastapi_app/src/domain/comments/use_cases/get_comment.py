from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.schemas.comments import CommentResponse, CommentListResponse
from fastapi import HTTPException, status


class GetCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()

    async def get_by_id(self, comment_id: int) -> CommentResponse:
        try:
            with self._database.session() as session:
                comment = self._repo.get_by_id(session, comment_id)
                if not comment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Комментарий не найден"
                    )
                return CommentResponse.model_validate(comment)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении комментария по ID: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_all(self, skip: int = 0, limit: int = 100) -> CommentListResponse:
        try:
            with self._database.session() as session:
                comments, total = self._repo.get_all(session, skip, limit)
                return CommentListResponse(
                    items=[CommentResponse.model_validate(c) for c in comments],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении списка комментариев: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> CommentListResponse:
        try:
            with self._database.session() as session:
                comments, total = self._repo.get_by_post(session, post_id, skip, limit)
                return CommentListResponse(
                    items=[CommentResponse.model_validate(c) for c in comments],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении комментариев поста: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> CommentListResponse:
        try:
            with self._database.session() as session:
                comments, total = self._repo.get_by_author(session, author_id, skip, limit)
                return CommentListResponse(
                    items=[CommentResponse.model_validate(c) for c in comments],
                    total=total
                )

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при получении комментариев автора: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )