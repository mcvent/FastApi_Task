from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging
logger = logging.getLogger(__name__)


class DeleteCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()

    async def execute(self, comment_id: int, current_user: dict) -> bool:
        try:
            async with self._database.session() as session:
                comment = await self._repo.get_by_id(session, comment_id)
                if not comment:
                    raise NotFoundException(
                        resource="Comment",
                        field="id",
                        value=comment_id
                    )

                # Проверка: только автор комментария или админ могут удалять
                is_author = comment.author_id == current_user.get("id")
                is_admin = current_user.get("is_superuser", False)

                if not (is_author or is_admin):
                    raise ForbiddenError(
                        message="Только автор комментария или администратор могут удалять комментарии",
                        required_role="comment_author_or_admin",
                        user_role="admin" if is_admin else "user" if not is_author else "other",
                        details={
                            "comment_author_id": comment.author_id,
                            "current_user_id": current_user.get("id"),
                            "is_author": is_author,
                            "is_admin": is_admin
                        }
                    )

                success = await self._repo.delete(session, comment_id)
                await session.commit()
                return success

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteCommentUseCase"
            e.details["comment_id"] = comment_id
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении комментария: {str(e)}",
                details={"use_case": "DeleteCommentUseCase", "comment_id": comment_id}
            )