from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.exceptions import NotFoundException, DatabaseException

class DeletePostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()

    async def execute(self, post_id: int) -> bool:
        try:
            with self._database.session() as session:
                post = self._repo.get_by_id(session, post_id)
                if not post:
                    raise NotFoundException(
                        resource="Post",
                        field="id",
                        value=post_id
                    )

                success = self._repo.delete(session, post_id)
                session.commit()
                return success

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeletePostUseCase"
            e.details["post_id"] = post_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении поста: {str(e)}",
                details={"use_case": "DeletePostUseCase", "post_id": post_id}
            )