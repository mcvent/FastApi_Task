from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.comment_image import CommentImageRepository
from src.schemas.comments import CommentImagesListResponse, CommentImageResponse
from src.exceptions import (
    CommentNotFoundByIdException,
    ImageNotFoundException,
    DatabaseException,
    AppException
)
from src.infrastructure.postgres.repositories.comments import CommentRepository
from fastapi.responses import FileResponse
import os


class GetCommentImagesUseCase:
    def __init__(self):
        self._database = database
        self._comment_repo = CommentRepository()
        self._image_repo = CommentImageRepository()
        self.image_folder = "static/images/comments"

    async def execute(self, comment_id: int) -> CommentImagesListResponse:
        try:
            async with self._database.session() as session:
                comment = await self._comment_repo.get_by_id(session, comment_id)
                if not comment:
                    raise CommentNotFoundByIdException(comment_id)

                images = await self._image_repo.get_by_comment(session, comment_id)

                return CommentImagesListResponse(
                    items=[
                        CommentImageResponse(
                            id=img.id,
                            image_path=img.image_path
                        ) for img in images
                    ],
                    total=len(images)
                )
        except CommentNotFoundByIdException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetCommentImagesUseCase"
            e.details["method"] = "execute"
            e.details["comment_id"] = comment_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка изображений комментария: {str(e)}",
                details={"use_case": "GetCommentImagesUseCase", "comment_id": comment_id}
            )

    async def get_by_id(self, comment_id: int, image_id: int) -> FileResponse:
        try:
            async with self._database.session() as session:
                comment = await self._comment_repo.get_by_id(session, comment_id)
                if not comment:
                    raise CommentNotFoundByIdException(comment_id)

                image = await self._image_repo.get_by_id(session, image_id)
                if not image or image.comment_id != comment_id:
                    raise ImageNotFoundException(image_id)

                full_image_path = os.path.join(self.image_folder, image.image_path)

                if not os.path.exists(full_image_path):
                    raise ImageNotFoundException()

                return FileResponse(full_image_path, media_type="image/jpeg")

        except (CommentNotFoundByIdException, ImageNotFoundException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetCommentImagesUseCase"
            e.details["method"] = "get_by_id"
            e.details["comment_id"] = comment_id
            e.details["image_id"] = image_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении изображения комментария: {str(e)}",
                details={
                    "use_case": "GetCommentImagesUseCase",
                    "comment_id": comment_id,
                    "image_id": image_id
                }
            )