from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from fastapi import HTTPException, status


class DeletePostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()

    async def execute(self, post_id: int) -> bool:
        try:
            with self._database.session() as session:
                post = self._repo.get_by_id(session, post_id)
                if not post:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Пост с ID {post_id} не найден"
                    )

                success = self._repo.delete(session, post_id)
                session.commit()
                return success

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при удалении поста: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )