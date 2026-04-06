from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.schemas.comments import CommentUpdate, CommentResponse
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError


class UpdateCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()

    async def execute(self, comment_id: int, update_data: CommentUpdate, current_user: dict) -> CommentResponse:
        try:
            with self._database.session() as session:
                comment = self._repo.get_by_id(session, comment_id)
                if not comment:
                    raise NotFoundException(
                        resource="Comment",
                        field="id",
                        value=comment_id
                    )

                # Проверка: только автор комментария может редактировать
                print (current_user.get("id"))
                if comment.author_id != current_user.get("id"):
                    raise ForbiddenError(
                        message="Только автор комментария может его редактировать",
                        required_role="comment_author",
                        user_role="other_user",
                        details={"comment_author_id": comment.author_id, "current_user_id": current_user.get("id")}
                    )

                updated_comment = self._repo.update(
                    session,
                    comment_id,
                    update_data.model_dump(exclude_unset=True)
                )
                session.commit()

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
                message=f"Странная ошибка при обновлении комментария: {str(e)}",
                details={"use_case": "UpdateCommentUseCase", "comment_id": comment_id}
            )