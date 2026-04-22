from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.posts import PostResponse, PostUpdate
from src.exceptions import NotFoundException, DatabaseException, ForbiddenError
import logging
logger = logging.getLogger(__name__)

class UpdatePostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()
        self._category_repo = CategoryRepository()
        self._location_repo = LocationRepository()

    async def execute(self, post_id: int, update_data: PostUpdate, current_user: dict) -> PostResponse:
        try:
            with self._database.session() as session:
                # Проверяем, существует ли пост
                existing_post = self._repo.get_by_id(session, post_id)
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
                        category = self._category_repo.get_by_id(session, update_data.category_id)
                        if not category:
                            raise NotFoundException(
                                resource="Category",
                                field="id",
                                value=update_data.category_id
                            )

                # Если меняется локация, проверяем её существование
                if update_data.location_id is not None and update_data.location_id != existing_post.location_id:
                    if update_data.location_id:
                        location = self._location_repo.get_by_id(session, update_data.location_id)
                        if not location:
                            raise NotFoundException(
                                resource="Location",
                                field="id",
                                value=update_data.location_id
                            )

                # Обновляем пост
                updated_post = self._repo.update(
                    session,
                    post_id,
                    update_data.model_dump(exclude_unset=True)
                )
                session.commit()

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