from uuid import uuid4
import shutil
import os
from fastapi import UploadFile

from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.schemas.posts import PostImageResponse
from src.exceptions import UploadFileIsNotImageException, PostNotFoundByIdException, ForbiddenError
import logging
logger = logging.getLogger(__name__)

class AddPostImageUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()
        self.image_folder = "static/images"

        # Создаем папку, если её нет
        os.makedirs(self.image_folder, exist_ok=True)

    async def execute(self, post_id: int, image: UploadFile, current_user: dict) -> PostImageResponse:
        """Добавляет изображение к посту и сохраняет путь в БД"""

        # Проверяем расширение файла
        allowed_extensions = ["jpeg", "jpg", "png"]
        file_extension = image.filename.split(".")[-1].lower()

        if file_extension not in allowed_extensions:
            raise UploadFileIsNotImageException()

        with self._database.session() as session:
            # Проверяем существование поста
            post = self._repo.get_by_id(session, post_id)
            if not post:
                raise PostNotFoundByIdException(post_id)

            # Проверка прав: только автор
            if post.author_id != current_user.get("id"):
                raise ForbiddenError("Только автор может добавлять изображения к посту")

            # Генерируем уникальное имя файла
            new_image_name = f"post_{post_id}_{uuid4()}.{file_extension}"
            new_image_path = os.path.join(self.image_folder, new_image_name)

            # Сохраняем файл
            with open(new_image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

            # Обновляем запись в БД - сохраняем путь к изображению
            post.image = new_image_name
            session.commit()

            return PostImageResponse(image_path=new_image_name)