from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.posts import PostResponse, PostCreate
from src.exceptions import NotFoundException, DatabaseException
from datetime import datetime

class CreatePostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()
        self._user_repo = UserRepository()
        self._category_repo = CategoryRepository()
        self._location_repo = LocationRepository()

    async def execute(self, post_data: PostCreate) -> PostResponse:
        try:
            with self._database.session() as session:
                # Проверяем существование автора
                author = self._user_repo.get_by_id(session, post_data.author_id)
                if not author:
                    raise NotFoundException(
                        resource="User",
                        field="id",
                        value=post_data.author_id
                    )

                # Проверяем существование категории (если указана)
                if post_data.category_id:
                    category = self._category_repo.get_by_id(session, post_data.category_id)
                    if not category:
                        raise NotFoundException(
                            resource="Category",
                            field="id",
                            value=post_data.category_id
                        )

                # Проверяем существование локации (если указана)
                if post_data.location_id:
                    location = self._location_repo.get_by_id(session, post_data.location_id)
                    if not location:
                        raise NotFoundException(
                            resource="Location",
                            field="id",
                            value=post_data.location_id
                        )

                # Создаем пост
                post_dict = post_data.model_dump()
                post_dict["created_at"] = datetime.now()

                new_post = self._repo.create(session, post_dict)
                session.commit()

                return PostResponse.model_validate(new_post)

        except NotFoundException:
            raise
        except DatabaseException as e:
            e.details["use_case"] = "CreatePostUseCase"
            e.details["author_id"] = post_data.author_id
            if post_data.category_id:
                e.details["category_id"] = post_data.category_id
            if post_data.location_id:
                e.details["location_id"] = post_data.location_id
            raise
        except Exception as e:
            raise DatabaseException(
                message=f"Странная ошибка при создании поста: {str(e)}",
                details={
                    "use_case": "CreatePostUseCase",
                    "author_id": post_data.author_id
                }
            )