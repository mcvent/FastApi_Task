from uuid import uuid4
import shutil
import os
from fastapi import UploadFile

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.post_image import PostImageRepository
from src.schemas.posts import PostImageResponse
from src.exceptions import UploadFileIsNotImageException, PostNotFoundByIdException, ForbiddenError
import logging

logger = logging.getLogger(__name__)


class AddPostImageUseCase:
    def __init__(self):
        self._database = database
        self._post_repo = PostRepository()
        self._image_repo = PostImageRepository()
        self.image_folder = "static/images"

        # Создаем папку, если её нет
        os.makedirs(self.image_folder, exist_ok=True)

    async def execute(self, post_id: int, image: UploadFile, current_user: dict) -> PostImageResponse:
        """Добавляет изображение к посту (поддерживает несколько изображений)"""

        # Проверяем расширение файла
        allowed_extensions = ["jpeg", "jpg", "png"]
        file_extension = image.filename.split(".")[-1].lower()

        if file_extension not in allowed_extensions:
            raise UploadFileIsNotImageException()

        async with self._database.session() as session:
            # Проверяем существование поста
            post = await self._post_repo.get_by_id(session, post_id)
            if not post:
                raise PostNotFoundByIdException(post_id)

            # Проверка прав: только автор
            if post.author_id != current_user.get("id"):
                raise ForbiddenError("Только автор может добавлять изображения к посту")

            # Получаем текущие изображения для определения порядка
            existing_images = await self._image_repo.get_by_post(session, post_id)
            next_order = len(existing_images)

            # Генерируем уникальное имя файла
            new_image_name = f"post_{post_id}_{uuid4()}.{file_extension}"
            new_image_path = os.path.join(self.image_folder, new_image_name)

            # Сохраняем файл
            with open(new_image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            # Сохраняем запись в БД (НЕ обновляем поле image в посте!)
            new_image = await self._image_repo.create(
                session,
                post_id=post_id,
                image_path=new_image_name,
                order=next_order
            )
            await session.commit()

            logger.info(f"Добавлено изображение {new_image_name} к посту {post_id} (порядок: {next_order})")

            return PostImageResponse(id=new_image.id,
                                     image_path=new_image.image_path,
                                     order=new_image.order)