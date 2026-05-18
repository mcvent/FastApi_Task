from uuid import uuid4
import shutil
import os
from fastapi import UploadFile

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.comments import CommentRepository
from src.infrastructure.postgres.repositories.comment_image import CommentImageRepository
from src.schemas.comments import CommentImageResponse
from src.exceptions import (
    UploadFileIsNotImageException,
    CommentNotFoundByIdException,
    ForbiddenError,
    DatabaseException
)
import logging

logger = logging.getLogger(__name__)


class AddCommentImageUseCase:
    def __init__(self):
        self._database = database
        self._comment_repo = CommentRepository()
        self._image_repo = CommentImageRepository()
        self.image_folder = "static/images/comments"

        os.makedirs(self.image_folder, exist_ok=True)

    async def execute(self, comment_id: int, image: UploadFile, current_user: dict) -> CommentImageResponse:
        allowed_extensions = ["jpeg", "jpg", "png"]
        file_extension = image.filename.split(".")[-1].lower()

        if file_extension not in allowed_extensions:
            raise UploadFileIsNotImageException()

        try:
            async with self._database.session() as session:
                comment = await self._comment_repo.get_by_id(session, comment_id)
                if not comment:
                    raise CommentNotFoundByIdException(comment_id)

                if comment.author_id != current_user.get("id"):
                    raise ForbiddenError("Только автор может добавлять изображения к комментарию")

                new_image_name = f"comment_{comment_id}_{uuid4()}.{file_extension}"
                new_image_path = os.path.join(self.image_folder, new_image_name)

                with open(new_image_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)

                new_image = await self._image_repo.create(session, comment_id, new_image_name)
                await session.commit()

                logger.info(f"Добавлено изображение {new_image_name} к комментарию {comment_id}")

                return CommentImageResponse(
                    id=new_image.id,
                    image_path=new_image.image_path
                )
        except (CommentNotFoundByIdException, ForbiddenError, UploadFileIsNotImageException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "AddCommentImageUseCase"
            e.details["comment_id"] = comment_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при добавлении изображения к комментарию: {str(e)}",
                details={"use_case": "AddCommentImageUseCase", "comment_id": comment_id}
            )