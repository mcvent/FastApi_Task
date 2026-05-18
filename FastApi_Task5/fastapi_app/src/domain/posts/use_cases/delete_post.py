from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging

logger = logging.getLogger(__name__)


class DeletePostUseCase:
    def __init__(
        self,
        session: AsyncSession,
        repo: PostRepository,
        comment_repo: CommentRepository
    ):
        self._session = session
        self._repo = repo
        self._comment_repo = comment_repo

    async def execute(self, post_id: int, current_user: dict) -> bool:
        try:
            post = await self._repo.get_by_id(self._session, post_id)
            if not post:
                raise NotFoundException(
                    resource="Post",
                    field="id",
                    value=post_id
                )

            # Проверка: только автор поста или админ могут удалять
            is_author = post.author_id == current_user.get("id")
            is_admin = current_user.get("is_superuser", False)

            if not (is_author or is_admin):
                raise ForbiddenError(
                    message="Только автор поста или администратор могут удалять посты",
                    required_role="post_author_or_admin",
                    user_role="admin" if is_admin else "user" if not is_author else "other",
                    details={
                        "post_author_id": post.author_id,
                        "current_user_id": current_user.get("id"),
                        "is_author": is_author,
                        "is_admin": is_admin
                    }
                )

            # Удаляем все комментарии к посту
            comments_deleted = await self._comment_repo.delete_by_post_id(self._session, post_id)

            # Удаляем пост
            success = await self._repo.delete(self._session, post_id)
            await self._session.commit()

            print(f"Удален пост {post_id} и {comments_deleted} комментариев к нему")
            return success

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeletePostUseCase"
            e.details["post_id"] = post_id
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении поста: {str(e)}",
                details={"use_case": "DeletePostUseCase", "post_id": post_id}
            )