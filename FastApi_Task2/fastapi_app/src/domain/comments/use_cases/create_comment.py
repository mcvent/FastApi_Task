from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.comments import CommentRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.schemas.comments import CommentCreate, CommentResponse
from fastapi import HTTPException, status
from datetime import datetime


class CreateCommentUseCase:
    def __init__(self):
        self._database = database
        self._repo = CommentRepository()
        self._user_repo = UserRepository()
        self._post_repo = PostRepository()


    async def execute(self, comment_data: CommentCreate
    ) -> CommentResponse:
        try:
            with self._database.session() as session:
                author = self._user_repo.get_by_id(session, comment_data.author_id)
                if not author:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Автор с ID {comment_data.author_id} не найден"
                    )

                post = self._post_repo.get_by_id(session, comment_data.post_id)
                if not post:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Пост с ID {comment_data.post_id} не найден"
                    )

                comment_dict = comment_data.model_dump()
                comment_dict["created_at"] = datetime.now()

                comment = self._repo.create(session, comment_dict)
                session.commit()

                return CommentResponse.model_validate(comment)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при создании комментария: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )