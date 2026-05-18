from fastapi.responses import FileResponse
import os
from typing import List

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.post_image import PostImageRepository
from src.exceptions import PostNotFoundByIdException, PostHasNoImageException, ImageNotFoundException, DatabaseException
from src.schemas.posts import PostImageResponse, PostImagesListResponse
import logging

logger = logging.getLogger(__name__)


class GetPostImageUseCase:
    def __init__(self):
        self._database = database
        self._post_repo = PostRepository()
        self._image_repo = PostImageRepository()
        self.image_folder = "static/images"

    async def execute(self, post_id: int) -> FileResponse:
        try:
            async with self._database.session() as session:
                post = await self._post_repo.get_by_id(session, post_id)
                if not post:
                    raise PostNotFoundByIdException(post_id)

                if not post.image:
                    raise PostHasNoImageException()

                full_image_path = os.path.join(self.image_folder, post.image)

                if not os.path.exists(full_image_path):
                    raise PostHasNoImageException()

                return FileResponse(full_image_path, media_type="image/jpeg")
        except (PostNotFoundByIdException, PostHasNoImageException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetPostImageUseCase"
            e.details["method"] = "execute"
            e.details["post_id"] = post_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении основного изображения: {str(e)}",
                details={"use_case": "GetPostImageUseCase", "post_id": post_id}
            )

    async def get_all_images(self, post_id: int) -> PostImagesListResponse:
        try:
            async with self._database.session() as session:
                post = await self._post_repo.get_by_id(session, post_id)
                if not post:
                    raise PostNotFoundByIdException(post_id)

                images = await self._image_repo.get_by_post(session, post_id)

                return PostImagesListResponse(
                    items=[
                        PostImageResponse(
                            id=img.id,
                            image_path=img.image_path,
                            order=img.order
                        ) for img in images
                    ],
                    total=len(images)
                )
        except PostNotFoundByIdException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetPostImageUseCase"
            e.details["method"] = "get_all_images"
            e.details["post_id"] = post_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении списка изображений: {str(e)}",
                details={"use_case": "GetPostImageUseCase", "post_id": post_id}
            )

    async def get_image_by_id(self, post_id: int, image_id: int) -> FileResponse:
        try:
            async with self._database.session() as session:
                post = await self._post_repo.get_by_id(session, post_id)
                if not post:
                    raise PostNotFoundByIdException(post_id)

                image = await self._image_repo.get_by_id(session, image_id)
                if not image or image.post_id != post_id:
                    raise ImageNotFoundException(image_id)

                full_image_path = os.path.join(self.image_folder, image.image_path)

                if not os.path.exists(full_image_path):
                    raise PostHasNoImageException()

                return FileResponse(full_image_path, media_type="image/jpeg")
        except (PostNotFoundByIdException, ImageNotFoundException, PostHasNoImageException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "GetPostImageUseCase"
            e.details["method"] = "get_image_by_id"
            e.details["post_id"] = post_id
            e.details["image_id"] = image_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при получении изображения поста: {str(e)}",
                details={"use_case": "GetPostImageUseCase", "post_id": post_id, "image_id": image_id}
            )