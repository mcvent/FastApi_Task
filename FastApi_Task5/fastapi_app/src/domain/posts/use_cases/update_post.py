from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.postgres.repositories.posts import PostRepository
from src.infrastructure.postgres.repositories.categories import CategoryRepository
from src.infrastructure.postgres.repositories.locations import LocationRepository
from src.schemas.posts import PostResponse, PostUpdate
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging

logger = logging.getLogger(__name__)


class UpdatePostUseCase:
    def __init__(
        self,
        session: AsyncSession,
        repo: PostRepository,
        category_repo: CategoryRepository,
        location_repo: LocationRepository
    ):
        self._session = session
        self._repo = repo
        self._category_repo = category_repo
        self._location_repo = location_repo

    async def execute(self, post_id: int, update_data: PostUpdate, current_user: dict) -> PostResponse:
        try:
            # Проверяем, существует ли пост
            existing_post = await self._repo.get_by_id(self._session, post_id)
            if not existing_post:
                raise NotFoundException(
                    resource="Post",
                    field="id",
                    value=post_id
                )

            # Проверка: только автор поста может редактировать
            if existing_post.author_id != current_user.get("id"):
                raise ForbiddenError(
                    message="Только автор поста может его редактировать",
                    required_role="post_author",
                    user_role="other_user",
                    details={"post_author_id": existing_post.author_id, "current_user_id": current_user.get("id")}
                )

            # Если меняется категория, проверяем её существование
            if update_data.category_id is not None and update_data.category_id != existing_post.category_id:
                if update_data.category_id:
                    category = await self._category_repo.get_by_id(self._session, update_data.category_id)
                    if not category:
                        raise NotFoundException(
                            resource="Category",
                            field="id",
                            value=update_data.category_id
                        )

            # Если меняется локация, проверяем её существование
            if update_data.location_id is not None and update_data.location_id != existing_post.location_id:
                if update_data.location_id:
                    location = await self._location_repo.get_by_id(self._session, update_data.location_id)
                    if not location:
                        raise NotFoundException(
                            resource="Location",
                            field="id",
                            value=update_data.location_id
                        )

            # Обновляем пост
            updated_post = await self._repo.update(
                self._session,
                post_id,
                update_data.model_dump(exclude_unset=True)
            )
            await self._session.commit()

            return PostResponse.model_validate(updated_post)

        except (NotFoundException, ForbiddenError):
            raise
        except DatabaseException as e:
            e.details["use_case"] = "UpdatePostUseCase"
            e.details["post_id"] = post_id
            e.details["user_id"] = current_user.get("id")
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при обновлении поста: {str(e)}",
                details={"use_case": "UpdatePostUseCase", "post_id": post_id}
            )