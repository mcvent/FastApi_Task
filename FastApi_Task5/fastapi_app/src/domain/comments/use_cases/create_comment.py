from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.schemas.comments import CommentCreate, CommentResponse
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
from datetime import datetime


class CreateCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()
        self._user_repo = UserRepository()
        self._post_repo = PostRepository()

    async def execute(self, comment_data: CommentCreate, current_user: dict) -> CommentResponse:
        try:
            # Проверка: только авторизованные пользователи могут создавать комментарии
            if not current_user:
                raise ForbiddenError(
                    message="Только авторизованные пользователи могут создавать комментарии",
                    required_role="authenticated",
                    user_role="anonymous"
                )

            with self._database.session() as session:
                # Проверяем существование поста
                post = self._post_repo.get_by_id(session, comment_data.post_id)
                if not post:
                    raise NotFoundException(
                        resource="Post",
                        field="id",
                        value=comment_data.post_id
                    )

                # Используем ID текущего пользователя, а не из запроса
                comment_dict = comment_data.model_dump()
                comment_dict["author_id"] = current_user.get("id")  # <-- Берем из токена
                comment_dict["created_at"] = datetime.now()

                new_comment = self._repo.create(session, comment_dict)
                session.commit()

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
                message=f"Странная ошибка при создании комментария: {str(e)}",
                details={
                    "use_case": "CreateCommentUseCase",
                    "post_id": comment_data.post_id
                }
            )