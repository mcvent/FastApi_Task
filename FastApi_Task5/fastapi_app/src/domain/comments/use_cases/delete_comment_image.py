import os
from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.comment_image import CommentImageRepository
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.exceptions import CommentNotFoundByIdException, ImageNotFoundException, ForbiddenError, DatabaseException


class DeleteCommentImageUseCase:
    def __init__(self):
        self._database = database
        self._comment_repo = CommentRepository()
        self._image_repo = CommentImageRepository()
        self.image_folder = "static/images/comments"

    async def execute(self, comment_id: int, image_id: int, current_user: dict) -> None:
        try:
            async with self._database.session() as session:
                comment = await self._comment_repo.get_by_id(session, comment_id)
                if not comment:
                    raise CommentNotFoundByIdException(comment_id)

                if comment.author_id != current_user.get("id"):
                    raise ForbiddenError("Только автор может удалять изображения комментария")

                image = await self._image_repo.get_by_id(session, image_id)
                if not image or image.comment_id != comment_id:
                    raise ImageNotFoundException(image_id)

                file_path = os.path.join(self.image_folder, image.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

                await self._image_repo.delete(session, image_id)
                await session.commit()
        except (CommentNotFoundByIdException, ForbiddenError, ImageNotFoundException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeleteCommentImageUseCase"
            e.details["comment_id"] = comment_id
            e.details["image_id"] = image_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении изображения комментария: {str(e)}",
                details={"use_case": "DeleteCommentImageUseCase", "comment_id": comment_id, "image_id": image_id}
            )