from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.schemas.comments import CommentCreate, CommentResponse
from src.exceptions import NotFoundException, DatabaseException
from datetime import datetime

class CreateCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()
        self._user_repo = UserRepository()
        self._post_repo = PostRepository()

    async def execute(self, comment_data: CommentCreate) -> CommentResponse:
        try:
            with self._database.session() as session:
                # Проверяем существование автора
                author = self._user_repo.get_by_id(session, comment_data.author_id)
                if not author:
                    raise NotFoundException(
                        resource="User",
                        field="id",
                        value=comment_data.author_id
                    )

                # Проверяем существование поста
                post = self._post_repo.get_by_id(session, comment_data.post_id)
                if not post:
                    raise NotFoundException(
                        resource="Post",
                        field="id",
                        value=comment_data.post_id
                    )

                comment_dict = comment_data.model_dump()
                comment_dict["created_at"] = datetime.now()

                new_comment = self._repo.create(session, comment_dict)
                session.commit()

                return CommentResponse.model_validate(new_comment)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreateCommentUseCase"
            e.details["author_id"] = comment_data.author_id
            e.details["post_id"] = comment_data.post_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при создании комментария: {str(e)}",
                details={
                    "use_case": "CreateCommentUseCase",
                    "author_id": comment_data.author_id,
                    "post_id": comment_data.post_id
                }
            )