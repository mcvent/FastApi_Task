from fastapi import HTTPException, status
from src.infrastructure.sqlite.database import database
from src.infrastructure.sqlite.repositories.posts import PostRepository
from src.infrastructure.sqlite.repositories.users import UserRepository
from src.infrastructure.sqlite.repositories.categories import CategoryRepository
from src.infrastructure.sqlite.repositories.locations import LocationRepository
from src.schemas.posts import PostResponse, PostUpdate


class UpdatePostUseCase:
    def __init__(self):
        self._database = database
        self._repo = PostRepository()
        self._user_repo = UserRepository()
        self._category_repo = CategoryRepository()
        self._location_repo = LocationRepository()

    async def execute(self, post_id: int, update_data: PostUpdate) -> PostResponse:
        """Обновить пост"""
        try:
            with self._database.session() as session:
                # Проверяем, существует ли пост
                existing_post = self._repo.get_by_id(session, post_id)
                if not existing_post:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Пост с ID {post_id} не найден"
                    )


                # Если меняется категория, проверяем её существование
                if update_data.category_id is not None and update_data.category_id != existing_post.category_id:
                    if update_data.category_id:  # Если не None, проверяем существование
                        from src.infrastructure.sqlite.repositories.categories import CategoryRepository
                        category_repo = CategoryRepository()
                        category = category_repo.get_by_id(session, update_data.category_id)
                        if not category:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Категория с ID {update_data.category_id} не найдена"
                            )

                # Если меняется локация, проверяем её существование
                if update_data.location_id is not None and update_data.location_id != existing_post.location_id:
                    if update_data.location_id:
                        from src.infrastructure.sqlite.repositories.locations import LocationRepository
                        location_repo = LocationRepository()
                        location = location_repo.get_by_id(session, update_data.location_id)
                        if not location:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Локация с ID {update_data.location_id} не найдена"
                            )

                # Обновляем пост
                updated_post = self._repo.update(
                    session,
                    post_id,
                    update_data.model_dump(exclude_unset=True)
                )
                session.commit()

                return PostResponse.model_validate(updated_post)

        except HTTPException:
            raise
        except Exception as e:
            print(f"Ошибка при обновлении поста: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )