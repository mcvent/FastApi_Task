from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.infrastructure.postgres.repositories.users import UserRepository
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.schemas.comments import CommentCreate, CommentResponse
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CreateCommentUseCase:
    def __init__(
        self,
        session: AsyncSession,
        repo: CommentRepository,
        user_repo: UserRepository,
        post_repo: PostRepository
    ):
        self._session = session
        self._repo = repo
        self._user_repo = user_repo
        self._post_repo = post_repo

    async def execute(self, comment_data: CommentCreate, current_user: dict) -> CommentResponse:
        try:
            if not current_user:
                raise ForbiddenError(
                    message="Только авторизованные пользователи могут создавать комментарии",
                    required_role="authenticated",
                    user_role="anonymous"
                )

            # Проверяем существование поста
            post = await self._post_repo.get_by_id(self._session, comment_data.post_id)
            if not post:
                raise NotFoundException(
                    resource="Post",
                    field="id",
                    value=comment_data.post_id
                )

            comment_dict = comment_data.model_dump()
            comment_dict["author_id"] = current_user.get("id")
            comment_dict["created_at"] = datetime.utcnow()

            new_comment = await self._repo.create(self._session, comment_dict)
            await self._session.commit()

            return CommentResponse.model_validate(new_comment)

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreateCommentUseCase"
            e.details["post_id"] = comment_data.post_id
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при создании комментария: {str(e)}",
                details={
                    "use_case": "CreateCommentUseCase",
                    "post_id": comment_data.post_id
                }
            )