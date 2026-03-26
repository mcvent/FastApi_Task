from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.exceptions import NotFoundException, DatabaseException

class DeleteCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()

    async def execute(self, comment_id: int) -> bool:
        try:
            with self._database.session() as session:
                comment = self._repo.get_by_id(session, comment_id)
                if not comment:
                    raise NotFoundException(
                        resource="Comment",
                        field="id",
                        value=comment_id
                    )

                success = self._repo.delete(session, comment_id)
                session.commit()
                return success

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteCommentUseCase"
            e.details["comment_id"] = comment_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении комментария: {str(e)}",
                details={"use_case": "DeleteCommentUseCase", "comment_id": comment_id}
            )