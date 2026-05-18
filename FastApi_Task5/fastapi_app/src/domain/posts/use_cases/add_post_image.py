from uuid import uuid4
import shutil
import os
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.post_image import PostImageRepository
from src.schemas.posts import PostImageResponse
from src.exceptions import UploadFileIsNotImageException, PostNotFoundByIdException, ForbiddenError, DatabaseException
import logging

logger = logging.getLogger(__name__)


class AddPostImageUseCase:
    def __init__(
        self,
        session: AsyncSession,
        post_repo: PostRepository,
        image_repo: PostImageRepository
    ):
        self._session = session
        self._post_repo = post_repo
        self._image_repo = image_repo
        self.image_folder = "static/images"

        os.makedirs(self.image_folder, exist_ok=True)

    async def execute(self, post_id: int, image: UploadFile, current_user: dict) -> PostImageResponse:
        allowed_extensions = ["jpeg", "jpg", "png"]
        file_extension = image.filename.split(".")[-1].lower()

        if file_extension not in allowed_extensions:
            raise UploadFileIsNotImageException()

        try:
            post = await self._post_repo.get_by_id(self._session, post_id)
            if not post:
                raise PostNotFoundByIdException(post_id)

            if post.author_id != current_user.get("id"):
                raise ForbiddenError("Только автор может добавлять изображения к посту")

            existing_images = await self._image_repo.get_by_post(self._session, post_id)
            next_order = len(existing_images)

            new_image_name = f"post_{post_id}_{uuid4()}.{file_extension}"
            new_image_path = os.path.join(self.image_folder, new_image_name)

            with open(new_image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            new_image = await self._image_repo.create(
                self._session,
                post_id=post_id,
                image_path=new_image_name,
                order=next_order
            )
            await self._session.commit()

            logger.info(f"Добавлено изображение {new_image_name} к посту {post_id} (порядок: {next_order})")

            return PostImageResponse(
                id=new_image.id,
                image_path=new_image.image_path,
                order=new_image.order
            )
        except (PostNotFoundByIdException, ForbiddenError, UploadFileIsNotImageException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "AddPostImageUseCase"
            e.details["post_id"] = post_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при добавлении изображения к посту: {str(e)}",
                details={"use_case": "AddPostImageUseCase", "post_id": post_id}
            )