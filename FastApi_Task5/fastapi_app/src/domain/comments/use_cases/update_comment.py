from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.schemas.comments import CommentUpdate, CommentResponse
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging

logger = logging.getLogger(__name__)


class UpdateCommentUseCase:
    def __init__(self, session: AsyncSession, repo: CommentRepository):
        self._session = session
        self._repo = repo

    async def execute(self, comment_id: int, update_data: CommentUpdate, current_user: dict) -> CommentResponse:
        try:
            comment = await self._repo.get_by_id(self._session, comment_id)
            if not comment:
                raise NotFoundException(
                    resource="Comment",
                    field="id",
                    value=comment_id
                )

            if comment.author_id != current_user.get("id"):
                raise ForbiddenError(
                    message="Только автор комментария может его редактировать",
                    required_role="comment_author",
                    user_role="other_user",
                    details={"comment_author_id": comment.author_id, "current_user_id": current_user.get("id")}
                )

            updated_comment = await self._repo.update(
                self._session,
                comment_id,
                update_data.model_dump(exclude_unset=True)
            )
            await self._session.commit()

            return CommentResponse.model_validate(updated_comment)

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "UpdateCommentUseCase"
            e.details["comment_id"] = comment_id
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при обновлении комментария: {str(e)}",
                details={"use_case": "UpdateCommentUseCase", "comment_id": comment_id}
            )