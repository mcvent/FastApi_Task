import os

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.post_image import PostImageRepository
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.exceptions import ImageNotFoundException, ForbiddenError


class DeletePostImageUseCase:
    def __init__(self):
        self._database = database
        self._post_repo = PostRepository()
        self._image_repo = PostImageRepository()
        self.image_folder = "static/images"

    async def execute(self, post_id: int, image_id: int, current_user: dict) -> None:
        async with self._database.session() as session:
            # Проверяем пост
            post = await self._post_repo.get_by_id(session, post_id)
            if not post:
                raise PostNotFoundByIdException(post_id)

            # Проверка прав
            if post.author_id != current_user.get("id"):
                raise ForbiddenError("Только автор может удалять изображения")

            # Получаем изображение
            image = await self._image_repo.get_by_id(session, image_id)
            if not image or image.post_id != post_id:
                raise ImageNotFoundException(image_id)

            # Удаляем файл
            file_path = os.path.join(self.image_folder, image.image_path)
            if os.path.exists(file_path):
                os.remove(file_path)

            # Удаляем запись из БД
            await self._image_repo.delete(session, image_id)
            await session.commit()