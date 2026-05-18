import os
from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.post_image import PostImageRepository
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.exceptions import ImageNotFoundException, ForbiddenError, PostNotFoundByIdException, DatabaseException


class DeletePostImageUseCase:
    def __init__(self):
        self._database = database
        self._post_repo = PostRepository()
        self._image_repo = PostImageRepository()
        self.image_folder = "static/images"

    async def execute(self, post_id: int, image_id: int, current_user: dict) -> None:
        try:
            async with self._database.session() as session:
                post = await self._post_repo.get_by_id(session, post_id)
                if not post:
                    raise PostNotFoundByIdException(post_id)

                if post.author_id != current_user.get("id"):
                    raise ForbiddenError("Только автор может удалять изображения")

                image = await self._image_repo.get_by_id(session, image_id)
                if not image or image.post_id != post_id:
                    raise ImageNotFoundException(image_id)

                file_path = os.path.join(self.image_folder, image.image_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

                await self._image_repo.delete(session, image_id)
                await session.commit()
        except (PostNotFoundByIdException, ForbiddenError, ImageNotFoundException):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "DeletePostImageUseCase"
            e.details["post_id"] = post_id
            e.details["image_id"] = image_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при удалении изображения поста: {str(e)}",
                details={"use_case": "DeletePostImageUseCase", "post_id": post_id, "image_id": image_id}
            )