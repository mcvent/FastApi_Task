from fastapi.responses import FileResponse
import os

from src.infrastructure.postgres.database import database
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.exceptions import PostNotFoundByIdException, PostHasNoImageException
import logging
logger = logging.getLogger(__name__)

class GetPostImageUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()
        self.image_folder = "static/images"

    async def execute(self, post_id: int) -> FileResponse:
        async with self._database.session() as session:
            post = await self._repo.get_by_id(session, post_id)

            if not post:
                raise PostNotFoundByIdException(post_id)

            if not post.image:
                raise PostHasNoImageException()

            full_image_path = os.path.join(self.image_folder, post.image)

            if not os.path.exists(full_image_path):
                raise PostHasNoImageException()

            return FileResponse(full_image_path, media_type="image/jpeg")