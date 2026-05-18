from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.users import UserRepository
from src.infrastructure.postgres.repositories.categories import CategoryRepository
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.schemas.posts import PostResponse, PostCreate
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CreatePostUseCase:
    def __init__(
        self,
        session: AsyncSession,
        repo: PostRepository,
        user_repo: UserRepository,
        category_repo: CategoryRepository,
        location_repo: LocationRepository
    ):
        self._session = session
        self._repo = repo
        self._user_repo = user_repo
        self._category_repo = category_repo
        self._location_repo = location_repo

    async def execute(self, post_data: PostCreate, current_user: dict) -> PostResponse:
        try:
            if not current_user:
                raise ForbiddenError(
                    message="Только авторизованные пользователи могут создавать посты",
                    required_role="authenticated",
                    user_role="anonymous"
                )

            # Проверяем категорию (если указана)
            if post_data.category_id:
                category = await self._category_repo.get_by_id(self._session, post_data.category_id)
                if not category:
                    raise NotFoundException(
                        resource="Category",
                        field="id",
                        value=post_data.category_id
                    )

            # Проверяем локацию (если указана)
            if post_data.location_id:
                location = await self._location_repo.get_by_id(self._session, post_data.location_id)
                if not location:
                    raise NotFoundException(
                        resource="Location",
                        field="id",
                        value=post_data.location_id
                    )

            # Создаем пост
            post_dict = post_data.model_dump()
            post_dict["author_id"] = current_user.get("id")
            post_dict["created_at"] = datetime.now()

            new_post = await self._repo.create(self._session, post_dict)
            await self._session.commit()

            return PostResponse.model_validate(new_post)

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreatePostUseCase"
            e.details["user_id"] = current_user.get("id")
            if post_data.category_id:
                e.details["category_id"] = post_data.category_id
            if post_data.location_id:
                e.details["location_id"] = post_data.location_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Ошибка при создании поста: {str(e)}",
                details={
                    "use_case": "CreatePostUseCase",
                    "user_id": current_user.get("id")
                }
            )