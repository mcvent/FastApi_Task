from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.schemas.comments import CommentUpdate, CommentResponse
from fastapi import HTTPException, status


class UpdateCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()

    async def execute(self, comment_id: int, update_data: CommentUpdate
    ) -> CommentResponse:
        try:
            with self._database.session() as session:
                comment = self._repo.get_by_id(session, comment_id)
                if not comment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Комментарий не найден"
                    )

                comment = self._repo.update(session, comment_id, update_data.model_dump(exclude_unset=True))
                session.commit()

                return CommentResponse.model_validate(comment)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при обновлении комментария: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )